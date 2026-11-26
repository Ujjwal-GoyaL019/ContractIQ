import threading
import uuid
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timezone, date
import pandas as pd
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models.product import Product
from app.db.models.sales_history import SalesHistory
from app.db.models.forecast import DemandForecast
from app.db.models.inventory import Inventory
from app.services.forecasting.prophet_model import ProphetForecaster
from app.services.forecasting.lightgbm_model import LightGBMForecaster
from app.services.forecasting.evaluator import ForecastEvaluator
from app.services.risk_engine.stockout_risk import stockout_calculator
from app.core.cache import cache_manager
from app.core.logging import logger


class ForecastJobRegistry:
    """
    Thread-safe registry for asynchronous background forecasting tasks.
    Enables status querying, error logging, and duplicate job suppression.
    """
    def __init__(self):
        self._jobs: Dict[str, Dict[str, Any]] = {}
        self._in_flight: Dict[str, str] = {}  # key: f"{sku}:{model_type}" -> job_id
        self._lock = threading.RLock()

    def register_job(self, sku: str, model_type: str, horizon_days: int) -> Tuple[str, bool]:
        with self._lock:
            key = f"{sku}:{model_type.lower()}"
            if key in self._in_flight:
                existing_id = self._in_flight[key]
                return existing_id, False  # Existing in-flight job

            job_id = str(uuid.uuid4())
            self._jobs[job_id] = {
                "job_id": job_id,
                "sku": sku,
                "model_type": model_type,
                "horizon_days": horizon_days,
                "status": "PENDING",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "started_at": None,
                "completed_at": None,
                "error": None,
                "metrics": None
            }
            self._in_flight[key] = job_id
            return job_id, True

    def set_running(self, job_id: str):
        with self._lock:
            if job_id in self._jobs:
                self._jobs[job_id]["status"] = "RUNNING"
                self._jobs[job_id]["started_at"] = datetime.now(timezone.utc).isoformat()

    def set_completed(self, job_id: str, metrics: Optional[Dict[str, Any]] = None):
        with self._lock:
            if job_id in self._jobs:
                job = self._jobs[job_id]
                job["status"] = "COMPLETED"
                job["completed_at"] = datetime.now(timezone.utc).isoformat()
                job["metrics"] = metrics
                key = f"{job['sku']}:{job['model_type'].lower()}"
                self._in_flight.pop(key, None)

    def set_failed(self, job_id: str, error_msg: str):
        with self._lock:
            if job_id in self._jobs:
                job = self._jobs[job_id]
                job["status"] = "FAILED"
                job["completed_at"] = datetime.now(timezone.utc).isoformat()
                job["error"] = error_msg
                key = f"{job['sku']}:{job['model_type'].lower()}"
                self._in_flight.pop(key, None)

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            return self._jobs.get(job_id)

    def list_jobs(self, limit: int = 20) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self._jobs.values())[-limit:]


job_registry = ForecastJobRegistry()
Tuple_Job = Any


def run_sku_forecast_job(
    sku: str,
    model_type: str = "prophet",
    horizon_days: int = 30,
    db: Optional[Session] = None,
    job_id: Optional[str] = None
):
    """
    Executes forecast model fitting, saves results to demand_forecasts table,
    updates dynamic inventory risk scores, and invalidates relevant caches.
    """
    if job_id:
        job_registry.set_running(job_id)

    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    try:
        product = db.query(Product).filter(Product.sku == sku).first()
        if not product:
            err = f"Product SKU {sku} not found for forecasting."
            logger.warning(err)
            if job_id:
                job_registry.set_failed(job_id, err)
            return

        sales_records = (
            db.query(SalesHistory)
            .filter(SalesHistory.product_id == product.id)
            .order_by(SalesHistory.sales_date.asc())
            .all()
        )

        if not sales_records or len(sales_records) < 5:
            err = f"Insufficient sales history for SKU {sku} (minimum 5 records required)."
            logger.warning(err)
            if job_id:
                job_registry.set_failed(job_id, err)
            return

        data = [
            {
                "sales_date": s.sales_date,
                "quantity_sold": s.quantity_sold,
                "is_promotion": s.is_promotion,
                "unit_price": s.unit_price,
            }
            for s in sales_records
        ]
        df = pd.DataFrame(data)

        # Select model
        if model_type.lower() == "lightgbm":
            forecaster = LightGBMForecaster()
            forecaster_cls = LightGBMForecaster
        else:
            forecaster = ProphetForecaster()
            forecaster_cls = ProphetForecaster

        # Backtest metrics
        metrics = ForecastEvaluator.backtest_model(
            forecaster_cls=forecaster_cls,
            df=df,
            test_days=min(14, len(df) // 4)
        )

        # Fit & forecast full series
        forecast_df = forecaster.fit_predict(df, horizon_days=horizon_days)

        # Delete existing forecasts for this SKU and model
        db.query(DemandForecast).filter(
            DemandForecast.product_id == product.id,
            DemandForecast.model_type == model_type
        ).delete()

        # Save new forecast records
        for _, row in forecast_df.iterrows():
            f_date = datetime.strptime(row["ds"], "%Y-%m-%d").date()
            record = DemandForecast(
                product_id=product.id,
                forecast_date=f_date,
                model_type=model_type,
                predicted_demand=float(row["yhat"]),
                lower_bound=float(row["yhat_lower"]),
                upper_bound=float(row["yhat_upper"]),
                mape=metrics["mape"],
                rmse=metrics["rmse"],
                mae=metrics["mae"],
            )
            db.add(record)

        # Update inventory dynamic risk fields
        if product.inventory:
            future_points = forecast_df.tail(horizon_days)
            avg_daily_demand = float(future_points["yhat"].mean()) or 1.0

            risk_eval = stockout_calculator.calculate_stockout_risk(
                current_stock=product.inventory.current_stock,
                allocated_stock=product.inventory.allocated_stock,
                incoming_stock=product.inventory.incoming_stock,
                lead_time_days=product.lead_time_days,
                forecasted_daily_demand=avg_daily_demand,
                safety_stock=product.min_safety_stock
            )
            product.inventory.stockout_risk_score = risk_eval["stockout_risk_score"]
            product.inventory.days_of_supply = risk_eval["days_of_supply"]
            product.inventory.urgency_status = risk_eval["urgency_status"]

        db.commit()

        # Invalidate affected cache tags
        cache_manager.invalidate_tag(f"forecast:{sku}")
        cache_manager.invalidate_tag("risk:summary")
        cache_manager.invalidate_tag("inventory:list")

        logger.info(f"Forecast job completed for SKU {sku} ({model_type}). MAPE: {metrics['mape']}%, RMSE: {metrics['rmse']}")
        if job_id:
            job_registry.set_completed(job_id, metrics)

    except Exception as e:
        logger.error(f"Error in forecast job for SKU {sku}: {e}")
        db.rollback()
        if job_id:
            job_registry.set_failed(job_id, str(e))
    finally:
        if close_db:
            db.close()


def run_all_forecasts_job(model_type: str = "prophet", horizon_days: int = 30):
    db = SessionLocal()
    try:
        products = db.query(Product).all()
        logger.info(f"Triggering batch forecasting for {len(products)} products using {model_type}...")
        for p in products:
            run_sku_forecast_job(sku=p.sku, model_type=model_type, horizon_days=horizon_days, db=db)
    finally:
        db.close()
