from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.db.models.product import Product
from app.db.models.inventory import Inventory
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.schemas.supplier import SupplierResponse
from app.core.exceptions import EntityNotFoundException

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=List[ProductResponse])
def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Product)
    if category:
        query = query.filter(Product.category == category)
        
    products = query.offset(skip).limit(limit).all()
    results = []
    for p in products:
        supplier_resp = SupplierResponse.model_validate(p.supplier) if p.supplier else None
        p_dict = {
            "id": p.id,
            "sku": p.sku,
            "name": p.name,
            "description": p.description,
            "category": p.category,
            "unit_of_measure": p.unit_of_measure,
            "unit_cost": p.unit_cost,
            "unit_price": p.unit_price,
            "min_safety_stock": p.min_safety_stock,
            "target_service_level": p.target_service_level,
            "lead_time_days": p.lead_time_days,
            "supplier_id": p.supplier_id,
            "created_at": p.created_at,
            "updated_at": p.updated_at,
            "supplier": supplier_resp,
            "current_stock": p.inventory.current_stock if p.inventory else 0,
            "days_of_supply": p.inventory.days_of_supply if p.inventory else 0.0,
            "stockout_risk_score": p.inventory.stockout_risk_score if p.inventory else 0.0,
        }
        results.append(ProductResponse(**p_dict))
    return results


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product_in: ProductCreate, db: Session = Depends(get_db)):
    product = Product(**product_in.model_dump())
    db.add(product)
    db.flush()

    # Automatically create initial empty inventory record
    inventory = Inventory(
        product_id=product.id,
        current_stock=0,
        reorder_point=product.min_safety_stock * 2,
        reorder_quantity=max(100, product.min_safety_stock * 3)
    )
    db.add(inventory)
    db.commit()
    db.refresh(product)
    return ProductResponse.model_validate(product)


@router.get("/{sku}", response_model=ProductResponse)
def get_product_by_sku(sku: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.sku == sku).first()
    if not product:
        raise EntityNotFoundException("Product SKU", sku)

    supplier_resp = SupplierResponse.model_validate(product.supplier) if product.supplier else None
    p_dict = {
        "id": product.id,
        "sku": product.sku,
        "name": product.name,
        "description": product.description,
        "category": product.category,
        "unit_of_measure": product.unit_of_measure,
        "unit_cost": product.unit_cost,
        "unit_price": product.unit_price,
        "min_safety_stock": product.min_safety_stock,
        "target_service_level": product.target_service_level,
        "lead_time_days": product.lead_time_days,
        "supplier_id": product.supplier_id,
        "created_at": product.created_at,
        "updated_at": product.updated_at,
        "supplier": supplier_resp,
        "current_stock": product.inventory.current_stock if product.inventory else 0,
        "days_of_supply": product.inventory.days_of_supply if product.inventory else 0.0,
        "stockout_risk_score": product.inventory.stockout_risk_score if product.inventory else 0.0,
    }
    return ProductResponse(**p_dict)
