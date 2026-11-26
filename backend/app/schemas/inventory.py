from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.product import ProductResponse


class InventoryBase(BaseModel):
    product_id: str
    warehouse_code: str = Field("WH-MAIN", example="WH-MAIN")
    current_stock: int = Field(0, ge=0, example=350)
    allocated_stock: int = Field(0, ge=0, example=20)
    incoming_stock: int = Field(0, ge=0, example=150)
    reorder_point: int = Field(100, ge=0, example=120)
    reorder_quantity: int = Field(250, ge=1, example=300)


class InventoryUpdate(BaseModel):
    current_stock: Optional[int] = None
    allocated_stock: Optional[int] = None
    incoming_stock: Optional[int] = None
    reorder_point: Optional[int] = None
    reorder_quantity: Optional[int] = None


class InventoryResponse(InventoryBase):
    id: str
    created_at: datetime
    updated_at: datetime
    available_stock: int = 0
    stockout_risk_score: float = 0.0
    days_of_supply: float = 0.0
    urgency_status: str = "HEALTHY"
    product: Optional[ProductResponse] = None

    class Config:
        from_attributes = True
