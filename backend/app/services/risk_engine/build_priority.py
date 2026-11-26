from typing import Dict, Any, List
from app.services.risk_engine.stockout_risk import stockout_calculator
from app.services.risk_engine.supplier_risk import supplier_risk_evaluator


class BuildPriorityEngine:
    """
    Ranks SKUs and inventory reorders by combining time-series stockout probability,
    supplier disruption vulnerability, and financial exposure.
    """

    @staticmethod
    def evaluate_sku(
        sku: str,
        product_name: str,
        category: str,
        unit_cost: float,
        unit_price: float,
        current_stock: int,
        allocated_stock: int,
        incoming_stock: int,
        lead_time_days: int,
        safety_stock: int,
        forecasted_daily_demand: float,
        supplier_id: str,
        supplier_name: str,
        supplier_country: str,
        supplier_reliability: float,
        supplier_quality: float,
        reorder_quantity: int
    ) -> Dict[str, Any]:
        # 1. Calculate stockout metrics
        stockout_metrics = stockout_calculator.calculate_stockout_risk(
            current_stock=current_stock,
            allocated_stock=allocated_stock,
            incoming_stock=incoming_stock,
            lead_time_days=lead_time_days,
            forecasted_daily_demand=forecasted_daily_demand,
            safety_stock=safety_stock
        )

        # 2. Calculate supplier risk metrics
        supplier_metrics = supplier_risk_evaluator.calculate_supplier_risk(
            reliability_score=supplier_reliability,
            quality_score=supplier_quality,
            base_lead_time_days=lead_time_days,
            country=supplier_country,
            supplier_id=supplier_id,
            supplier_name=supplier_name
        )

        stockout_score = stockout_metrics["stockout_risk_score"]
        supplier_score = supplier_metrics["supplier_disruption_risk"]

        # 3. Composite Weighted Risk Index (60% stockout urgency + 40% supplier vulnerability)
        composite_score = round((stockout_score * 0.60) + (supplier_score * 0.40), 1)

        # Severity categorization
        if composite_score >= 70.0:
            severity = "CRITICAL"
        elif composite_score >= 45.0:
            severity = "HIGH"
        elif composite_score >= 25.0:
            severity = "MEDIUM"
        else:
            severity = "LOW"

        # Financial capital at risk
        financial_impact = round(stockout_metrics["lead_time_demand"] * unit_cost, 2)

        # Suggested actions
        all_reasons = []
        if stockout_metrics["net_margin"] < 0:
            all_reasons.append(f"Projected deficit of {abs(stockout_metrics['net_margin'])} units over lead time")
        all_reasons.extend(supplier_metrics["risk_reasons"])

        if severity == "CRITICAL":
            action = f"URGENT: Expedite purchase order for {max(reorder_quantity, stockout_metrics['recommended_reorder_units'])} units and check secondary sources."
        elif severity == "HIGH":
            action = f"Place standard reorder for {max(reorder_quantity, stockout_metrics['recommended_reorder_units'])} units to restore safety stock buffer."
        elif severity == "MEDIUM":
            action = "Monitor demand velocity; review upcoming order deliveries."
        else:
            action = "Inventory levels healthy; no immediate replenishment required."

        return {
            "sku": sku,
            "product_name": product_name,
            "category": category,
            "supplier_name": supplier_name,
            "supplier_country": supplier_country,
            "current_stock": current_stock,
            "incoming_stock": incoming_stock,
            "lead_time_days": lead_time_days,
            "forecasted_demand_lead_time": stockout_metrics["lead_time_demand"],
            "safety_stock": safety_stock,
            "projected_net_stock": stockout_metrics["net_margin"],
            "days_until_stockout": stockout_metrics["days_until_stockout"],
            "reorder_recommended_units": stockout_metrics["recommended_reorder_units"],
            "financial_impact_risk": financial_impact,
            "risk_breakdown": {
                "stockout_risk_score": stockout_score,
                "supplier_disruption_risk": supplier_score,
                "composite_risk_score": composite_score,
                "severity": severity
            },
            "risk_reasons": all_reasons,
            "suggested_action": action
        }


build_priority_engine = BuildPriorityEngine()
