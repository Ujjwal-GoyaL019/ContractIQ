from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from app.dependencies import get_db
from app.db.models.inventory import Inventory
from app.db.models.product import Product
from app.schemas.inventory import InventoryResponse, InventoryUpdate
from app.schemas.product import ProductResponse
from app.schemas.supplier import SupplierResponse
from app.core.exceptions import EntityNotFoundException
from app.core.cache import cache_manager

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get("", response_model=List[InventoryResponse])
def get_inventory_items(
    urgency_status: Optional[str] = None,
    warehouse_code: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    cache_key = f"inventory:items:{urgency_status or 'all'}:{warehouse_code or 'all'}:{skip}:{limit}"
    cached_data = cache_manager.get(cache_key)
    if cached_data is not None:
        return cached_data

    query = (
        db.query(Inventory)
        .options(
            joinedload(Inventory.product).joinedload(Product.supplier)
        )
    )

    if urgency_status:
        query = query.filter(Inventory.urgency_status == urgency_status.upper())
    if warehouse_code:
        query = query.filter(Inventory.warehouse_code == warehouse_code)

    items = query.offset(skip).limit(limit).all()
    results: List[InventoryResponse] = []

    for inv in items:
        p = inv.product
        prod_resp = None
        if p:
            sup_resp = SupplierResponse.model_validate(p.supplier) if p.supplier else None
            prod_resp = ProductResponse(
                id=p.id,
                sku=p.sku,
                name=p.name,
                description=p.description,
                category=p.category,
                unit_of_measure=p.unit_of_measure,
                unit_cost=p.unit_cost,
                unit_price=p.unit_price,
                min_safety_stock=p.min_safety_stock,
                target_service_level=p.target_service_level,
                lead_time_days=p.lead_time_days,
                supplier_id=p.supplier_id,
                created_at=p.created_at,
                updated_at=p.updated_at,
                supplier=sup_resp,
                current_stock=inv.current_stock,
                days_of_supply=inv.days_of_supply,
                stockout_risk_score=inv.stockout_risk_score
            )

        available_stock = max(0, inv.current_stock - inv.allocated_stock + inv.incoming_stock)
        results.append(
            InventoryResponse(
                id=inv.id,
                product_id=inv.product_id,
                warehouse_code=inv.warehouse_code,
                current_stock=inv.current_stock,
                allocated_stock=inv.allocated_stock,
                incoming_stock=inv.incoming_stock,
                available_stock=available_stock,
                reorder_point=inv.reorder_point,
                reorder_quantity=inv.reorder_quantity,
                stockout_risk_score=inv.stockout_risk_score,
                days_of_supply=inv.days_of_supply,
                urgency_status=inv.urgency_status,
                created_at=inv.created_at,
                updated_at=inv.updated_at,
                product=prod_resp
            )
        )

    cache_manager.set(cache_key, results, ttl_seconds=60.0, tags=["inventory:list"])
    return results


@router.put("/{product_sku}", response_model=InventoryResponse)
def update_inventory_levels(
    product_sku: str,
    inv_update: InventoryUpdate,
    db: Session = Depends(get_db)
):
    product = (
        db.query(Product)
        .options(joinedload(Product.inventory), joinedload(Product.supplier))
        .filter(Product.sku == product_sku)
        .first()
    )
    if not product or not product.inventory:
        raise EntityNotFoundException("Inventory for SKU", product_sku)

    inv = product.inventory
    update_data = inv_update.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(inv, k, v)

    db.commit()
    db.refresh(inv)

    # Invalidate all related caches immediately
    cache_manager.invalidate_tag("inventory:list")
    cache_manager.invalidate_tag("risk:summary")
    cache_manager.invalidate_tag(f"forecast:{product_sku}")

    available_stock = max(0, inv.current_stock - inv.allocated_stock + inv.incoming_stock)
    sup_resp = SupplierResponse.model_validate(product.supplier) if product.supplier else None
    prod_resp = ProductResponse(
        id=product.id,
        sku=product.sku,
        name=product.name,
        description=product.description,
        category=product.category,
        unit_of_measure=product.unit_of_measure,
        unit_cost=product.unit_cost,
        unit_price=product.unit_price,
        min_safety_stock=product.min_safety_stock,
        target_service_level=product.target_service_level,
        lead_time_days=product.lead_time_days,
        supplier_id=product.supplier_id,
        created_at=product.created_at,
        updated_at=product.updated_at,
        supplier=sup_resp,
        current_stock=inv.current_stock,
        days_of_supply=inv.days_of_supply,
        stockout_risk_score=inv.stockout_risk_score
    )

    return InventoryResponse(
        id=inv.id,
        product_id=inv.product_id,
        warehouse_code=inv.warehouse_code,
        current_stock=inv.current_stock,
        allocated_stock=inv.allocated_stock,
        incoming_stock=inv.incoming_stock,
        available_stock=available_stock,
        reorder_point=inv.reorder_point,
        reorder_quantity=inv.reorder_quantity,
        stockout_risk_score=inv.stockout_risk_score,
        days_of_supply=inv.days_of_supply,
        urgency_status=inv.urgency_status,
        created_at=inv.created_at,
        updated_at=inv.updated_at,
        product=prod_resp
    )
