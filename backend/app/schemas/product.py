from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.supplier import SupplierResponse


class ProductBase(BaseModel):
    sku: str = Field(..., example="SKU-MICRO-01")
    name: str = Field(..., example="Arm Cortex-M4 MCU 120MHz")
    description: Optional[str] = Field(None, example="High-performance embedded microcontroller")
    category: str = Field("Semiconductors", example="Semiconductors")
    unit_of_measure: str = Field("units", example="units")
    unit_cost: float = Field(0.0, ge=0.0, example=8.50)
    unit_price: float = Field(0.0, ge=0.0, example=16.00)
    min_safety_stock: int = Field(50, ge=0, example=100)
    target_service_level: float = Field(0.95, ge=0.5, le=0.999, example=0.95)
    lead_time_days: int = Field(14, ge=1, example=14)
    supplier_id: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    unit_of_measure: Optional[str] = None
    unit_cost: Optional[float] = None
    unit_price: Optional[float] = None
    min_safety_stock: Optional[int] = None
    target_service_level: Optional[float] = None
    lead_time_days: Optional[int] = None
    supplier_id: Optional[str] = None


class ProductResponse(ProductBase):
    id: str
    created_at: datetime
    updated_at: datetime
    supplier: Optional[SupplierResponse] = None
    current_stock: Optional[int] = 0
    days_of_supply: Optional[float] = 0.0
    stockout_risk_score: Optional[float] = 0.0

    class Config:
        from_attributes = True
