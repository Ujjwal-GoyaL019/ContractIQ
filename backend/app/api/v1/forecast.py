from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, date, timedelta
from fastapi import APIRouter, Depends, BackgroundTasks, Query
from sqlalchemy.orm import Session
import pandas as pd
from app.dependencies import get_db
from app.db.models.product import Product
from app.db.models.sales_history import SalesHistory
from app.db.models.forecast import DemandForecast
from app.schemas.forecast import ForecastPoint, ForecastTriggerRequest, ForecastResponse, BacktestMetrics
from app.workers.forecast_jobs import run_sku_forecast_job, run_all_forecasts_job, job_registry
from app.services.forecasting.prophet_model import ProphetForecaster
from app.services.forecasting.lightgbm_model import LightGBMForecaster
from app.services.forecasting.evaluator import ForecastEvaluator
from app.core.exceptions import EntityNotFoundException, ForecastingException
from app.core.cache import cache_manager

router = APIRouter(prefix="/forecast", tags=["Forecasting"])


@router.get("/{sku}", response_model=ForecastResponse)
def get_sku_forecast(
    sku: str,
    model_type: str = Query("prophet", pattern="^(prophet|lightgbm)$"),
    history_days: int = Query(60, ge=14, le=365),
    db: Session = Depends(get_db)
):
    cache_key = f"forecast:{sku}:{model_type}:{history_days}"
    cached_res = cache_manager.get(cache_key)
    if cached_res is not None:
        return cached_res

    product = db.query(Product).filter(Product.sku == sku).first()
    if not product:
        raise EntityNotFoundException("Product SKU", sku)

    # 1. Fetch historical sales points
    cutoff_date = date.today() - timedelta(days=history_days)
    sales = (
        db.query(SalesHistory)
        .filter(SalesHistory.product_id == product.id, SalesHistory.sales_date >= cutoff_date)
        .order_by(SalesHistory.sales_date.asc())
        .all()
    )

    history_points = [
        ForecastPoint(
            date=s.sales_date.strftime("%Y-%m-%d"),
            actual_demand=float(s.quantity_sold),
            predicted_demand=float(s.quantity_sold),
            lower_bound=float(s.quantity_sold),
            upper_bound=float(s.quantity_sold)
        )
        for s in sales
    ]

    # 2. Fetch stored forecast points
    stored_forecasts = (
        db.query(DemandForecast)
        .filter(
            DemandForecast.product_id == product.id,
            DemandForecast.model_type == model_type,
            DemandForecast.forecast_date >= date.today()
        )
        .order_by(DemandForecast.forecast_date.asc())
        .all()
    )

    # If no stored forecasts exist, trigger on the fly
    if not stored_forecasts:
        run_sku_forecast_job(sku=sku, model_type=model_type, horizon_days=30, db=db)
        stored_forecasts = (
            db.query(DemandForecast)
            .filter(
                DemandForecast.product_id == product.id,
                DemandForecast.model_type == model_type,
                DemandForecast.forecast_date >= date.today()
            )
            .order_by(DemandForecast.forecast_date.asc())
            .all()
        )

    forecast_points = [
        ForecastPoint(
            date=f.forecast_date.strftime("%Y-%m-%d"),
            predicted_demand=round(f.predicted_demand, 1),
            lower_bound=round(f.lower_bound, 1),
            upper_bound=round(f.upper_bound, 1),
            actual_demand=None
        )
        for f in stored_forecasts
    ]

    mape = stored_forecasts[0].mape if stored_forecasts else None
    rmse = stored_forecasts[0].rmse if stored_forecasts else None
    mae = stored_forecasts[0].mae if stored_forecasts else None
    total_demand = sum(p.predicted_demand for p in forecast_points)
    avg_demand = (total_demand / len(forecast_points)) if forecast_points else 0.0

    response = ForecastResponse(
        sku=product.sku,
        product_name=product.name,
        model_type=model_type,
        horizon_days=len(forecast_points),
        generated_at=datetime.now(timezone.utc),
        mape=mape,
        rmse=rmse,
        mae=mae,
        historical_points=history_points,
        forecast_points=forecast_points,
        total_forecasted_demand=round(total_demand, 1),
        average_daily_demand=round(avg_demand, 1)
    )

    cache_manager.set(cache_key, response, ttl_seconds=120.0, tags=[f"forecast:{sku}", "forecast:all"])
    return response


@router.post("/trigger")
def trigger_forecasting(
    req: ForecastTriggerRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    if req.sku:
        product = db.query(Product).filter(Product.sku == req.sku).first()
        if not product:
            raise EntityNotFoundException("Product SKU", req.sku)

        job_id, is_new = job_registry.register_job(
            sku=req.sku, model_type=req.model_type, horizon_days=req.horizon_days
        )
        if is_new:
            background_tasks.add_task(
                run_sku_forecast_job,
                sku=req.sku,
                model_type=req.model_type,
                horizon_days=req.horizon_days,
                job_id=job_id
            )
        return {
            "status": "accepted" if is_new else "already_running",
            "job_id": job_id,
            "message": f"Forecasting {'queued' if is_new else 'in-progress'} for SKU '{req.sku}' ({req.model_type})"
        }
    else:
        background_tasks.add_task(
            run_all_forecasts_job, model_type=req.model_type, horizon_days=req.horizon_days
        )
        return {"status": "accepted", "message": f"Batch forecasting queued for all SKUs ({req.model_type})"}


@router.get("/jobs/{job_id}")
def get_forecast_job_status(job_id: str):
    job = job_registry.get_job(job_id)
    if not job:
        raise EntityNotFoundException("Forecast Job", job_id)
    return job


@router.get("/jobs")
def list_forecast_jobs(limit: int = Query(20, ge=1, le=100)):
    return job_registry.list_jobs(limit=limit)


@router.get("/compare/{sku}", response_model=List[BacktestMetrics])
def compare_forecasting_models(sku: str, db: Session = Depends(get_db)):
    cache_key = f"forecast:compare:{sku}"
    cached_metrics = cache_manager.get(cache_key)
    if cached_metrics is not None:
        return cached_metrics

    product = db.query(Product).filter(Product.sku == sku).first()
    if not product:
        raise EntityNotFoundException("Product SKU", sku)

    sales = (
        db.query(SalesHistory)
        .filter(SalesHistory.product_id == product.id)
        .order_by(SalesHistory.sales_date.asc())
        .all()
    )

    if len(sales) < 15:
        raise ForecastingException("Insufficient historical demand data to compare models (min 15 records required).")

    df = pd.DataFrame([{"sales_date": s.sales_date, "quantity_sold": s.quantity_sold} for s in sales])
    test_days = min(14, len(df) // 4)

    prophet_metrics = ForecastEvaluator.backtest_model(
        forecaster_cls=ProphetForecaster, df=df, test_days=test_days
    )
    lgb_metrics = ForecastEvaluator.backtest_model(
        forecaster_cls=LightGBMForecaster, df=df, test_days=test_days
    )

    metrics_list = [
        BacktestMetrics(
            model_type="prophet",
            mape=prophet_metrics["mape"],
            rmse=prophet_metrics["rmse"],
            mae=prophet_metrics["mae"],
            wape=prophet_metrics["wape"],
            sample_count=prophet_metrics["sample_count"]
        ),
        BacktestMetrics(
            model_type="lightgbm",
            mape=lgb_metrics["mape"],
            rmse=lgb_metrics["rmse"],
            mae=lgb_metrics["mae"],
            wape=lgb_metrics["wape"],
            sample_count=lgb_metrics["sample_count"]
        )
    ]

    cache_manager.set(cache_key, metrics_list, ttl_seconds=300.0, tags=[f"forecast:{sku}"])
    return metrics_list
