from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.db.models.supplier import Supplier
from app.db.models.product import Product
from app.db.models.document import SupplierDocument
from app.schemas.supplier import SupplierCreate, SupplierUpdate, SupplierResponse
from app.core.exceptions import EntityNotFoundException

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])


@router.get("", response_model=List[SupplierResponse])
def get_suppliers(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Supplier)
    if status:
        query = query.filter(Supplier.status == status)
    
    suppliers = query.offset(skip).limit(limit).all()
    results = []
    for s in suppliers:
        s_dict = {
            "id": s.id,
            "code": s.code,
            "name": s.name,
            "contact_email": s.contact_email,
            "contact_phone": s.contact_phone,
            "country": s.country,
            "base_lead_time_days": s.base_lead_time_days,
            "reliability_score": s.reliability_score,
            "quality_score": s.quality_score,
            "disruption_risk_score": s.disruption_risk_score,
            "payment_terms": s.payment_terms,
            "status": s.status,
            "notes": s.notes,
            "created_at": s.created_at,
            "updated_at": s.updated_at,
            "product_count": len(s.products),
            "document_count": len(s.documents),
        }
        results.append(SupplierResponse(**s_dict))
    return results


@router.post("", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
def create_supplier(supplier_in: SupplierCreate, db: Session = Depends(get_db)):
    supplier = Supplier(**supplier_in.model_dump())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return SupplierResponse.model_validate(supplier)


@router.get("/{supplier_id}", response_model=SupplierResponse)
def get_supplier(supplier_id: str, db: Session = Depends(get_db)):
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise EntityNotFoundException("Supplier", supplier_id)
    
    s_dict = {
        "id": supplier.id,
        "code": supplier.code,
        "name": supplier.name,
        "contact_email": supplier.contact_email,
        "contact_phone": supplier.contact_phone,
        "country": supplier.country,
        "base_lead_time_days": supplier.base_lead_time_days,
        "reliability_score": supplier.reliability_score,
        "quality_score": supplier.quality_score,
        "disruption_risk_score": supplier.disruption_risk_score,
        "payment_terms": supplier.payment_terms,
        "status": supplier.status,
        "notes": supplier.notes,
        "created_at": supplier.created_at,
        "updated_at": supplier.updated_at,
        "product_count": len(supplier.products),
        "document_count": len(supplier.documents),
    }
    return SupplierResponse(**s_dict)


@router.put("/{supplier_id}", response_model=SupplierResponse)
def update_supplier(supplier_id: str, supplier_in: SupplierUpdate, db: Session = Depends(get_db)):
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise EntityNotFoundException("Supplier", supplier_id)
    
    update_data = supplier_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(supplier, field, val)

    db.commit()
    db.refresh(supplier)
    return SupplierResponse.model_validate(supplier)
