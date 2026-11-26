import pytest
from app.services.risk_engine.stockout_risk import stockout_calculator
from app.services.risk_engine.supplier_risk import supplier_risk_evaluator
from app.services.risk_engine.build_priority import build_priority_engine


def test_stockout_risk_calculator_critical():
    # Low stock, high demand -> CRITICAL
    res = stockout_calculator.calculate_stockout_risk(
        current_stock=20,
        allocated_stock=10,
        incoming_stock=0,
        lead_time_days=21,
        forecasted_daily_demand=15.0, # 315 needed over lead time!
        safety_stock=50
    )
    assert res["stockout_risk_score"] >= 70.0
    assert res["urgency_status"] in ["CRITICAL", "HIGH"]
    assert res["days_until_stockout"] < 5.0
    assert res["recommended_reorder_units"] > 300


def test_stockout_risk_calculator_healthy():
    # Healthy inventory
    res = stockout_calculator.calculate_stockout_risk(
        current_stock=500,
        allocated_stock=20,
        incoming_stock=200,
        lead_time_days=10,
        forecasted_daily_demand=10.0,
        safety_stock=50
    )
    assert res["stockout_risk_score"] <= 35.0
    assert res["urgency_status"] in ["HEALTHY", "LOW", "OVERSTOCKED"]


def test_supplier_risk_evaluator():
    res = supplier_risk_evaluator.calculate_supplier_risk(
        reliability_score=0.75,
        quality_score=0.88,
        base_lead_time_days=45,
        country="Overseas"
    )
    assert res["supplier_disruption_risk"] >= 25.0
    assert len(res["risk_reasons"]) >= 1


def test_build_priority_engine():
    res = build_priority_engine.evaluate_sku(
        sku="SKU-TEST-01",
        product_name="Test Sensor",
        category="Sensors",
        unit_cost=10.0,
        unit_price=25.0,
        current_stock=30,
        allocated_stock=10,
        incoming_stock=0,
        lead_time_days=20,
        safety_stock=50,
        forecasted_daily_demand=10.0,
        supplier_id="sup-test",
        supplier_name="Test Supplier",
        supplier_country="US",
        supplier_reliability=0.85,
        supplier_quality=0.92,
        reorder_quantity=200
    )
    assert "sku" in res
    assert "risk_breakdown" in res
    assert "composite_risk_score" in res["risk_breakdown"]
    assert "suggested_action" in res
    assert len(res["risk_reasons"]) >= 1
