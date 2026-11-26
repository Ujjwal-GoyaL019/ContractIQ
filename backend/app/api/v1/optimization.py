from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.db.models.product import Product
from app.db.models.supplier import Supplier
from app.db.models.inventory import Inventory
from app.core.cache import cache_manager
from app.core.exceptions import EntityNotFoundException
from app.services.optimization.supplier_optimizer import milp_optimizer, SupplierOption
from app.services.evaluation.benchmark_suite import benchmark_suite

router = APIRouter(prefix="/optimization", tags=["Prescriptive Optimization & AI Benchmarks"])


class CustomSupplierInput(BaseModel):
    supplier_id: str
    supplier_name: str
    supplier_code: str = "SUP-CUSTOM"
    country: str = "Global"
    unit_cost: float = Field(..., gt=0)
    surcharge_pct: float = Field(0.0, ge=0.0, le=100.0)
    lead_time_days: int = Field(14, ge=1, le=180)
    reliability_score: float = Field(0.95, ge=0.1, le=1.0)
    disruption_risk_score: float = Field(15.0, ge=0.0, le=100.0)
    moq: int = Field(50, ge=0)
    max_capacity: int = Field(5000, ge=1)
    fixed_order_cost: float = Field(150.0, ge=0.0)
    sla_penalty_rate: float = Field(0.015, ge=0.0, le=1.0)


class OptimizationRequest(BaseModel):
    sku: str = Field("SKU-LENS-4K", description="Target SKU to optimize procurement allocation for")
    required_quantity: Optional[int] = Field(None, ge=10, le=100000, description="Total replenishment units required (auto-derived if omitted)")
    risk_aversion_lambda: float = Field(1.5, ge=0.0, le=5.0, description="Weight on disruption/unreliability risk penalty (0=pure cost, 3+=high risk aversion)")
    max_single_supplier_share: float = Field(0.70, ge=0.35, le=1.0, description="Maximum fraction of total order allowed from any single vendor")
    target_lead_time_days: int = Field(18, ge=1, le=90, description="Desired delivery window before lead-time exposure penalty applies")
    custom_suppliers: Optional[List[CustomSupplierInput]] = None


# Contract-grounded dual-sourcing profiles linking DB suppliers to SKU-specific terms extracted from PDFs
SKU_CONTRACT_TERMS: Dict[str, Dict[str, Dict[str, Any]]] = {
    "SKU-LENS-4K": {
        "SUP-PACIFIC": {"unit_cost": 18.50, "surcharge_pct": 12.5, "moq": 100, "max_capacity": 1500, "fixed_cost": 220.0, "sla_penalty_rate": 0.0},
        "SUP-EUROOPTICS": {"unit_cost": 21.40, "surcharge_pct": 0.0, "moq": 100, "max_capacity": 1200, "fixed_cost": 180.0, "sla_penalty_rate": 0.02},
        "SUP-APEX": {"unit_cost": 22.80, "surcharge_pct": 0.0, "moq": 150, "max_capacity": 1000, "fixed_cost": 200.0, "sla_penalty_rate": 0.02},
    },
    "SKU-MCU-32B": {
        "SUP-APEX": {"unit_cost": 6.80, "surcharge_pct": 0.0, "moq": 250, "max_capacity": 2500, "fixed_cost": 150.0, "sla_penalty_rate": 0.02},
        "SUP-NORDIC": {"unit_cost": 7.35, "surcharge_pct": 0.0, "moq": 150, "max_capacity": 2000, "fixed_cost": 140.0, "sla_penalty_rate": 0.015},
        "SUP-EUROOPTICS": {"unit_cost": 7.90, "surcharge_pct": 0.0, "moq": 100, "max_capacity": 1200, "fixed_cost": 180.0, "sla_penalty_rate": 0.02},
    },
    "SKU-BLE-SOC": {
        "SUP-NORDIC": {"unit_cost": 4.20, "surcharge_pct": 0.0, "moq": 150, "max_capacity": 3000, "fixed_cost": 120.0, "sla_penalty_rate": 0.015},
        "SUP-APEX": {"unit_cost": 4.65, "surcharge_pct": 0.0, "moq": 200, "max_capacity": 2000, "fixed_cost": 160.0, "sla_penalty_rate": 0.02},
        "SUP-TITAN": {"unit_cost": 5.10, "surcharge_pct": 0.0, "moq": 100, "max_capacity": 1500, "fixed_cost": 100.0, "sla_penalty_rate": 0.01},
    },
    "SKU-ENC-IP67": {
        "SUP-TITAN": {"unit_cost": 11.20, "surcharge_pct": 0.0, "moq": 100, "max_capacity": 2500, "fixed_cost": 100.0, "sla_penalty_rate": 0.01},
        "SUP-NORDIC": {"unit_cost": 12.10, "surcharge_pct": 0.0, "moq": 100, "max_capacity": 1800, "fixed_cost": 140.0, "sla_penalty_rate": 0.015},
        "SUP-EUROOPTICS": {"unit_cost": 12.60, "surcharge_pct": 0.0, "moq": 100, "max_capacity": 1500, "fixed_cost": 160.0, "sla_penalty_rate": 0.02},
    },
}


@router.post("/allocate")
def optimize_supplier_allocation(req: OptimizationRequest, db: Session = Depends(get_db)):
    """
    Solves the Multi-Supplier Mixed-Integer Linear Programming (MILP) order allocation problem.
    Balances direct landed unit cost, contractual surcharges, MOQ constraints, lead times,
    and supplier disruption risk to recommend an optimal split purchase order.
    """
    if req.custom_suppliers:
        supplier_options = [
            SupplierOption(**s.model_dump()) for s in req.custom_suppliers
        ]
        demand_qty = req.required_quantity or 500
        return milp_optimizer.solve(
            sku=req.sku,
            total_demand_qty=demand_qty,
            suppliers=supplier_options,
            risk_aversion_lambda=req.risk_aversion_lambda,
            max_single_supplier_share=req.max_single_supplier_share,
            target_lead_time_days=req.target_lead_time_days,
        )

    product = db.query(Product).filter(Product.sku == req.sku).first()
    if not product:
        raise EntityNotFoundException("Product", req.sku)

    inventory = db.query(Inventory).filter(Inventory.product_id == product.id).first()
    default_qty = max(300, int(inventory.reorder_quantity * 2)) if inventory else 500
    demand_qty = req.required_quantity or default_qty

    all_suppliers = db.query(Supplier).all()
    if not all_suppliers:
        raise EntityNotFoundException("Suppliers", "active catalog")

    terms_map = SKU_CONTRACT_TERMS.get(product.sku, {})
    supplier_options: List[SupplierOption] = []

    for idx, sup in enumerate(all_suppliers):
        if terms_map and sup.code not in terms_map:
            continue
        t = terms_map.get(sup.code, {})
        base_cost = t.get("unit_cost", round(product.unit_cost * (1.0 + 0.08 * idx), 2))
        supplier_options.append(
            SupplierOption(
                supplier_id=sup.id,
                supplier_name=sup.name,
                supplier_code=sup.code,
                country=sup.country or "Global",
                unit_cost=base_cost,
                surcharge_pct=t.get("surcharge_pct", 0.0),
                lead_time_days=sup.base_lead_time_days,
                reliability_score=sup.reliability_score,
                disruption_risk_score=sup.disruption_risk_score,
                moq=t.get("moq", 100),
                max_capacity=t.get("max_capacity", max(demand_qty, 2000)),
                fixed_order_cost=t.get("fixed_cost", 150.0),
                sla_penalty_rate=t.get("sla_penalty_rate", 0.015),
            )
        )

    # Fallback: if terms_map matched < 2 suppliers, include remaining catalog suppliers
    if len(supplier_options) < 2:
        existing_ids = {s.supplier_id for s in supplier_options}
        for idx, sup in enumerate(all_suppliers):
            if sup.id in existing_ids:
                continue
            supplier_options.append(
                SupplierOption(
                    supplier_id=sup.id,
                    supplier_name=sup.name,
                    supplier_code=sup.code,
                    country=sup.country or "Global",
                    unit_cost=round(product.unit_cost * (1.12 + 0.05 * idx), 2),
                    surcharge_pct=0.0,
                    lead_time_days=sup.base_lead_time_days,
                    reliability_score=sup.reliability_score,
                    disruption_risk_score=sup.disruption_risk_score,
                    moq=100,
                    max_capacity=max(demand_qty, 2000),
                    fixed_order_cost=150.0,
                )
            )

    result = milp_optimizer.solve(
        sku=product.sku,
        total_demand_qty=demand_qty,
        suppliers=supplier_options,
        risk_aversion_lambda=req.risk_aversion_lambda,
        max_single_supplier_share=req.max_single_supplier_share,
        target_lead_time_days=req.target_lead_time_days,
    )
    result["product_name"] = product.name
    result["category"] = product.category
    return result


@router.get("/evaluate")
def run_ai_evaluation_benchmarks(
    include_forecasting: bool = Query(True, description="Include holdout time-series backtest across SKUs"),
    test_days: int = Query(14, ge=7, le=30),
    force_refresh: bool = Query(False, description="Bypass cache and recompute full benchmarks"),
    db: Session = Depends(get_db),
):
    """
    Executes the Empirical AI Evaluation Benchmark Suite:
      1. RAG Ablation: Dense HNSW vs. Sparse BM25 vs. Hybrid RRF + Reranker (Hit@1, Hit@3, MRR, Precision@3)
      2. Time-Series Backtest: Naive MA-7 Baseline vs. Prophet vs. LightGBM Quantile (MAPE, RMSE, P90 Coverage)
    """
    cache_key = f"ai_benchmarks:{include_forecasting}:{test_days}"
    if not force_refresh:
        cached = cache_manager.get(cache_key)
        if cached is not None:
            return cached

    rag_report = benchmark_suite.evaluate_rag_retrieval(top_k=3)
    hallucination_report = benchmark_suite.evaluate_hallucination_guard()
    forecast_report = (
        benchmark_suite.evaluate_forecasting_models(db=db, test_days=test_days)
        if include_forecasting
        else None
    )

    payload = {
        "status": "completed",
        "rag_evaluation": rag_report,
        "hallucination_audit": hallucination_report,
        "forecasting_evaluation": forecast_report,
    }
    cache_manager.set(cache_key, payload, ttl_seconds=600, tags=["benchmarks"])
    return payload
