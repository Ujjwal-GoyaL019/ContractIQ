from datetime import date
from sqlalchemy import String, Float, Integer, Date, Boolean, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimeStampMixin


class SalesHistory(Base, TimeStampMixin):
    __tablename__ = "sales_history"
    __table_args__ = (
        Index("ix_sales_product_date", "product_id", "sales_date"),
    )

    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    sales_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    
    quantity_sold: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    unit_price: Mapped[float] = mapped_column(Float, default=0.0)
    is_promotion: Mapped[bool] = mapped_column(Boolean, default=False)
    is_holiday: Mapped[bool] = mapped_column(Boolean, default=False)
    had_stockout: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="sales_history")
