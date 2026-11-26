from typing import List, Optional
from sqlalchemy import String, Float, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimeStampMixin


class Product(Base, TimeStampMixin):
    __tablename__ = "products"

    sku: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(100), index=True, default="General")
    unit_of_measure: Mapped[str] = mapped_column(String(20), default="units")
    
    # Financials
    unit_cost: Mapped[float] = mapped_column(Float, default=0.0)
    unit_price: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Safety & lead time parameters
    min_safety_stock: Mapped[int] = mapped_column(Integer, default=50)
    target_service_level: Mapped[float] = mapped_column(Float, default=0.95)  # 95%
    lead_time_days: Mapped[int] = mapped_column(Integer, default=14)
    
    # Preferred Supplier
    supplier_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("suppliers.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    supplier: Mapped[Optional["Supplier"]] = relationship("Supplier", back_populates="products")
    inventory: Mapped[Optional["Inventory"]] = relationship("Inventory", back_populates="product", uselist=False, cascade="all, delete-orphan")
    sales_history: Mapped[List["SalesHistory"]] = relationship("SalesHistory", back_populates="product", cascade="all, delete-orphan")
    forecasts: Mapped[List["DemandForecast"]] = relationship("DemandForecast", back_populates="product", cascade="all, delete-orphan")
    order_items: Mapped[List["PurchaseOrderItem"]] = relationship("PurchaseOrderItem", back_populates="product")
