from sqlalchemy import String, Integer, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimeStampMixin


class Inventory(Base, TimeStampMixin):
    __tablename__ = "inventory"
    __table_args__ = (
        Index("ix_inventory_wh_urgency", "warehouse_code", "urgency_status"),
    )

    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    warehouse_code: Mapped[str] = mapped_column(String(50), default="WH-MAIN", index=True)
    
    # Quantities
    current_stock: Mapped[int] = mapped_column(Integer, default=0)
    allocated_stock: Mapped[int] = mapped_column(Integer, default=0)  # reserved for orders
    incoming_stock: Mapped[int] = mapped_column(Integer, default=0)   # in transit via open POs
    
    # Calculated / Configured Thresholds
    reorder_point: Mapped[int] = mapped_column(Integer, default=100)
    reorder_quantity: Mapped[int] = mapped_column(Integer, default=250)
    
    # Dynamic Risk Computed Fields
    stockout_risk_score: Mapped[float] = mapped_column(default=0.0)   # 0.0 - 100.0
    days_of_supply: Mapped[float] = mapped_column(default=30.0)       # current stock / daily avg demand
    urgency_status: Mapped[str] = mapped_column(String(50), default="HEALTHY") # CRITICAL, WARNING, LOW, HEALTHY, OVERSTOCKED

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="inventory")
