from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class RiskBreakdown(BaseModel):
    stockout_risk_score: float = Field(..., ge=0.0, le=100.0) # 0-100
    supplier_disruption_risk: float = Field(..., ge=0.0, le=100.0) # 0-100
    composite_risk_score: float = Field(..., ge=0.0, le=100.0) # 0-100
    severity: str = Field(..., example="CRITICAL") # CRITICAL, HIGH, MEDIUM, LOW


class SKURiskItem(BaseModel):
    sku: str
    product_name: str
    category: str
    supplier_name: str
    supplier_country: str
    
    # Quantities
    current_stock: int
    incoming_stock: int
    lead_time_days: int
    forecasted_demand_lead_time: float
    safety_stock: int
    
    # Computed metrics
    projected_net_stock: float
    days_until_stockout: float
    reorder_recommended_units: int
    financial_impact_risk: float
    
    # Risk Scores
    risk_breakdown: RiskBreakdown
    risk_reasons: List[str]
    suggested_action: str


class RiskSummaryResponse(BaseModel):
    total_skus: int
    critical_risk_count: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    total_capital_at_risk: float
    average_supplier_reliability: float
    items: List[SKURiskItem]
