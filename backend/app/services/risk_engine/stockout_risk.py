from typing import Dict, Any
import numpy as np


class StockoutRiskCalculator:
    """
    Evaluates inventory stockout vulnerability by comparing available stock + incoming orders
    against forecasted forward demand over supplier lead time + safety stock requirements.
    """

    @staticmethod
    def calculate_stockout_risk(
        current_stock: int,
        allocated_stock: int,
        incoming_stock: int,
        lead_time_days: int,
        forecasted_daily_demand: float,
        safety_stock: int
    ) -> Dict[str, Any]:
        # Net immediately available stock
        usable_current = max(0, current_stock - allocated_stock)
        total_pipeline_stock = usable_current + incoming_stock

        # Expected consumption over lead time
        lead_time_demand = max(1.0, forecasted_daily_demand * lead_time_days)
        required_buffer = lead_time_demand + safety_stock

        # Net surplus / deficit
        net_margin = total_pipeline_stock - required_buffer
        
        # Days of supply based on on-hand stock
        days_of_supply = round(usable_current / forecasted_daily_demand, 1) if forecasted_daily_demand > 0 else 999.0

        # Stockout Risk Score (0.0 to 100.0)
        if usable_current == 0 and incoming_stock == 0:
            risk_score = 100.0
            urgency = "CRITICAL"
        elif total_pipeline_stock < lead_time_demand:
            # Deficit: will run out before supplier order arrives
            deficit = lead_time_demand - total_pipeline_stock
            deficit_ratio = min(1.0, deficit / lead_time_demand)
            risk_score = round(70.0 + (deficit_ratio * 30.0), 1)
            urgency = "CRITICAL" if risk_score >= 85.0 else "HIGH"
        elif total_pipeline_stock < required_buffer:
            # Below safety stock buffer
            buffer_deficit = required_buffer - total_pipeline_stock
            ratio = min(1.0, buffer_deficit / (safety_stock if safety_stock > 0 else 1.0))
            risk_score = round(35.0 + (ratio * 35.0), 1)
            urgency = "HIGH" if risk_score >= 50.0 else "MEDIUM"
        elif usable_current > required_buffer * 3.0:
            # Overstocked
            risk_score = 5.0
            urgency = "OVERSTOCKED"
        else:
            # Healthy range
            margin_ratio = min(1.0, (total_pipeline_stock - required_buffer) / required_buffer)
            risk_score = round(max(0.0, 30.0 - (margin_ratio * 25.0)), 1)
            urgency = "HEALTHY" if risk_score <= 20.0 else "LOW"

        # Days until stockout estimate
        days_until_stockout = round(total_pipeline_stock / forecasted_daily_demand, 1) if forecasted_daily_demand > 0 else 999.0

        # Recommended replenishment quantity
        reorder_units = max(0, int(np.ceil(required_buffer - total_pipeline_stock)))

        return {
            "stockout_risk_score": float(risk_score),
            "urgency_status": urgency,
            "days_of_supply": float(days_of_supply),
            "days_until_stockout": float(days_until_stockout),
            "lead_time_demand": round(float(lead_time_demand), 1),
            "net_margin": round(float(net_margin), 1),
            "recommended_reorder_units": reorder_units,
        }


stockout_calculator = StockoutRiskCalculator()
