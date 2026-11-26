from typing import List, Optional
from datetime import date, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.dependencies import get_db
from app.db.models.product import Product
from app.db.models.sales_history import SalesHistory
from app.schemas.risk import SKURiskItem, RiskSummaryResponse
from app.services.risk_engine.build_priority import build_priority_engine
from app.core.cache import cache_manager

router = APIRouter(prefix="/risk", tags=["Risk Advisory"])


@router.get("", response_model=RiskSummaryResponse)
def get_risk_summary(
    severity: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    cache_key = f"risk:summary:{severity or 'all'}:{category or 'all'}"
    cached_data = cache_manager.get(cache_key)
    if cached_data is not None:
        return cached_data

    # 1. Single Eager-Loaded Query for all Products + Inventory + Supplier (0 N+1 overhead)
    products = (
        db.query(Product)
        .options(
            joinedload(Product.inventory),
            joinedload(Product.supplier)
        )
        .all()
    )

    # 2. Single Aggregated Demand Query for past 30 days across all products
    cutoff_date = date.today() - timedelta(days=30)
    demand_aggs = (
        db.query(
            SalesHistory.product_id,
            func.avg(SalesHistory.quantity_sold).label("avg_daily_demand")
        )
        .filter(SalesHistory.sales_date >= cutoff_date)
        .group_by(SalesHistory.product_id)
        .all()
    )
    demand_map = {row.product_id: float(row.avg_daily_demand or 5.0) for row in demand_aggs}

    risk_items: List[SKURiskItem] = []
    critical_count = 0
    high_count = 0
    medium_count = 0
    low_count = 0
    total_capital = 0.0
    supplier_reliabilities = []

    for prod in products:
        inv = prod.inventory
        sup = prod.supplier

        current_stock = inv.current_stock if inv else 0
        allocated_stock = inv.allocated_stock if inv else 0
        incoming_stock = inv.incoming_stock if inv else 0
        reorder_qty = inv.reorder_quantity if inv else 100

        # Supplier parameters
        sup_id = sup.id if sup else ""
        sup_name = sup.name if sup else "Unassigned Supplier"
        sup_country = sup.country if sup else "US"
        sup_reliability = sup.reliability_score if sup else 0.90
        sup_quality = sup.quality_score if sup else 0.95
        supplier_reliabilities.append(sup_reliability)

        # Average historical daily demand from pre-aggregated map
        avg_daily_demand = demand_map.get(prod.id, 5.0)

        item_dict = build_priority_engine.evaluate_sku(
            sku=prod.sku,
            product_name=prod.name,
            category=prod.category,
            unit_cost=prod.unit_cost,
            unit_price=prod.unit_price,
            current_stock=current_stock,
            allocated_stock=allocated_stock,
            incoming_stock=incoming_stock,
            lead_time_days=prod.lead_time_days,
            safety_stock=prod.min_safety_stock,
            forecasted_daily_demand=avg_daily_demand,
            supplier_id=sup_id,
            supplier_name=sup_name,
            supplier_country=sup_country,
            supplier_reliability=sup_reliability,
            supplier_quality=sup_quality,
            reorder_quantity=reorder_qty
        )

        item = SKURiskItem(**item_dict)
        sev = item.risk_breakdown.severity

        if sev == "CRITICAL":
            critical_count += 1
        elif sev == "HIGH":
            high_count += 1
        elif sev == "MEDIUM":
            medium_count += 1
        else:
            low_count += 1

        total_capital += item.financial_impact_risk

        # Filter check
        if severity and sev != severity.upper():
            continue
        if category and prod.category.lower() != category.lower():
            continue

        risk_items.append(item)

    # Sort descending by composite risk score
    risk_items.sort(key=lambda x: x.risk_breakdown.composite_risk_score, reverse=True)
    avg_rel = (sum(supplier_reliabilities) / len(supplier_reliabilities)) if supplier_reliabilities else 0.95

    response = RiskSummaryResponse(
        total_skus=len(products),
        critical_risk_count=critical_count,
        high_risk_count=high_count,
        medium_risk_count=medium_count,
        low_risk_count=low_count,
        total_capital_at_risk=round(total_capital, 2),
        average_supplier_reliability=round(avg_rel * 100, 1),
        items=risk_items
    )

    # Cache for 60 seconds under the 'risk:summary' namespace
    cache_manager.set(cache_key, response, ttl_seconds=60.0, tags=["risk:summary"])
    return response
