from typing import List, Optional, Dict, Any
from datetime import date, datetime
from pydantic import BaseModel, Field


class ForecastPoint(BaseModel):
    date: str
    predicted_demand: float
    lower_bound: float
    upper_bound: float
    actual_demand: Optional[float] = None


class ForecastTriggerRequest(BaseModel):
    sku: Optional[str] = Field(None, description="SKU code or None to forecast all SKUs")
    model_type: str = Field("prophet", description="'prophet' or 'lightgbm'")
    horizon_days: int = Field(30, ge=7, le=90, description="Forecast horizon in days")


class ForecastResponse(BaseModel):
    sku: str
    product_name: str
    model_type: str
    horizon_days: int
    generated_at: datetime
    mape: Optional[float] = None
    rmse: Optional[float] = None
    mae: Optional[float] = None
    historical_points: List[ForecastPoint] = []
    forecast_points: List[ForecastPoint] = []
    total_forecasted_demand: float = 0.0
    average_daily_demand: float = 0.0


class BacktestMetrics(BaseModel):
    model_type: str
    mape: float
    rmse: float
    mae: float
    wape: float
    sample_count: int
