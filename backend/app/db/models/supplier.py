from typing import List, Optional
from sqlalchemy import String, Float, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimeStampMixin


class Supplier(Base, TimeStampMixin):
    __tablename__ = "suppliers"

    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), index=True, nullable=False)
    contact_email: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    country: Mapped[str] = mapped_column(String(100), default="US")
    
    # Operational metrics
    base_lead_time_days: Mapped[int] = mapped_column(Integer, default=14)
    reliability_score: Mapped[float] = mapped_column(Float, default=0.95)  # 0.0 - 1.0 (on-time rate)
    quality_score: Mapped[float] = mapped_column(Float, default=0.98)      # 0.0 - 1.0 (defect-free rate)
    disruption_risk_score: Mapped[float] = mapped_column(Float, default=10.0) # 0.0 - 100.0
    
    payment_terms: Mapped[str] = mapped_column(String(100), default="Net 30")
    status: Mapped[str] = mapped_column(String(50), default="active")  # active, warning, restricted
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    products: Mapped[List["Product"]] = relationship("Product", back_populates="supplier")
    orders: Mapped[List["PurchaseOrder"]] = relationship("PurchaseOrder", back_populates="supplier", cascade="all, delete-orphan")
    documents: Mapped[List["SupplierDocument"]] = relationship("SupplierDocument", back_populates="supplier", cascade="all, delete-orphan")
