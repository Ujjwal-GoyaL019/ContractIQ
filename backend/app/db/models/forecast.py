from datetime import date, datetime
from typing import Optional
from sqlalchemy import String, Float, Date, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimeStampMixin


class DemandForecast(Base, TimeStampMixin):
    __tablename__ = "demand_forecasts"
    __table_args__ = (
        Index("ix_forecast_prod_model_date", "product_id", "model_type", "forecast_date"),
    )

    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    forecast_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    model_type: Mapped[str] = mapped_column(String(50), default="prophet") # prophet, lightgbm, ensemble
    
    # Forecasted Values
    predicted_demand: Mapped[float] = mapped_column(Float, nullable=False)
    lower_bound: Mapped[float] = mapped_column(Float, nullable=False)
    upper_bound: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Backtest Metrics & Meta
    run_timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    mape: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    rmse: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    mae: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="forecasts")
