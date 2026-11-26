from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class SupplierBase(BaseModel):
    code: str = Field(..., example="SUP-001")
    name: str = Field(..., example="Apex Microelectronics")
    contact_email: Optional[str] = Field(None, example="orders@apexmicro.com")
    contact_phone: Optional[str] = Field(None, example="+1-555-0199")
    country: str = Field("US", example="US")
    base_lead_time_days: int = Field(14, ge=1, example=14)
    reliability_score: float = Field(0.95, ge=0.0, le=1.0, example=0.95)
    quality_score: float = Field(0.98, ge=0.0, le=1.0, example=0.98)
    disruption_risk_score: float = Field(10.0, ge=0.0, le=100.0, example=15.0)
    payment_terms: str = Field("Net 30", example="Net 30")
    status: str = Field("active", example="active")
    notes: Optional[str] = None


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    country: Optional[str] = None
    base_lead_time_days: Optional[int] = None
    reliability_score: Optional[float] = None
    quality_score: Optional[float] = None
    disruption_risk_score: Optional[float] = None
    payment_terms: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class SupplierResponse(SupplierBase):
    id: str
    created_at: datetime
    updated_at: datetime
    product_count: Optional[int] = 0
    document_count: Optional[int] = 0

    class Config:
        from_attributes = True
