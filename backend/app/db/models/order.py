from datetime import date, datetime
from typing import List, Optional
from sqlalchemy import String, Float, Integer, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimeStampMixin


class PurchaseOrder(Base, TimeStampMixin):
    __tablename__ = "purchase_orders"

    order_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    supplier_id: Mapped[str] = mapped_column(String(36), ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False, index=True)
    
    order_date: Mapped[date] = mapped_column(Date, nullable=False)
    expected_delivery_date: Mapped[date] = mapped_column(Date, nullable=False)
    actual_delivery_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    status: Mapped[str] = mapped_column(String(50), default="PLACED") # PLACED, CONFIRMED, SHIPPED, DELIVERED, DELAYED, CANCELLED
    total_amount: Mapped[float] = mapped_column(Float, default=0.0)
    delay_days: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    supplier: Mapped["Supplier"] = relationship("Supplier", back_populates="orders")
    items: Mapped[List["PurchaseOrderItem"]] = relationship("PurchaseOrderItem", back_populates="order", cascade="all, delete-orphan")


class PurchaseOrderItem(Base, TimeStampMixin):
    __tablename__ = "purchase_order_items"

    order_id: Mapped[str] = mapped_column(String(36), ForeignKey("purchase_orders.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    
    quantity_ordered: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity_received: Mapped[int] = mapped_column(Integer, default=0)
    unit_price: Mapped[float] = mapped_column(Float, default=0.0)

    # Relationships
    order: Mapped["PurchaseOrder"] = relationship("PurchaseOrder", back_populates="items")
    product: Mapped["Product"] = relationship("Product", back_populates="order_items")
