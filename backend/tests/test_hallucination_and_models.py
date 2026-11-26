from datetime import date, timedelta
import numpy as np
import pandas as pd
import pytest

from app.services.rag.hallucination_guard import hallucination_guard, extract_factual_claims
from app.services.rag.generation import rag_service
from app.services.evaluation.benchmark_suite import (
    benchmark_suite,
    ADVERSARIAL_HALLUCINATION_TRAPS,
    GOLDEN_RAG_BENCHMARK,
)
from app.services.forecasting.evaluator import ForecastEvaluator
from app.services.forecasting.prophet_model import ProphetForecaster
from app.services.forecasting.lightgbm_model import LightGBMForecaster
from app.services.forecasting.multi_model_forecasters import (
    XGBoostForecaster,
    RandomForestForecaster,
    RidgeLagForecaster,
)


def test_claim_extractor_identifies_high_stakes_legal_facts():
    text = (
        "Under Section 7.2 for SKU-LENS-4K, EuroOptics charges $21.40 per unit with a 2.0% weekly penalty, "
        "18 calendar days lead time, ISO Class 5 cleanroom, and 100 DPPM quality ceiling."
    )
    claims = extract_factual_claims(text)
    lower_claims = [c.lower() for c in claims]
    assert "sku-lens-4k" in lower_claims
    assert "$21.40" in lower_claims
    assert "2.0%" in lower_claims
    assert "section 7.2" in lower_claims
    assert "iso class 5" in lower_claims
    assert any("18" in c and "day" in c for c in lower_claims)
    assert "100 dppm" in lower_claims


def test_post_generation_auditor_catches_fabricated_llm_hallucinations():
    """
    Proves that the post-generation factuality auditor passes 100% faithful outputs
    and catches fabricated numbers/SKUs/percentages injected by a hallucinating LLM.
    """
    source_snippets = [
        {
            "doc_title": "EuroOptics Secondary Qualification SLA",
            "supplier_name": "EuroOptics Precision GmbH",
            "page_number": 1,
            "content": (
                "EuroOptics is qualified for SKU-LENS-4K at $21.40 USD per unit with 18 calendar days lead time, "
                "ISO Class 5 cleanroom compliance, 0.02% defect tolerance, and 2.0% weekly late penalty."
            ),
        }
    ]

    # 1. Faithful grounded answer -> 100% verified
    faithful = (
        "For SKU-LENS-4K, EuroOptics charges $21.40 with an 18 calendar days lead time, "
        "ISO Class 5 cleanroom, 0.02% defect limit, and 2.0% late penalty."
    )
    ok_audit = hallucination_guard.verify_answer_grounding(faithful, source_snippets)
    assert ok_audit["is_grounded"] is True
    assert ok_audit["faithfulness_score"] == 1.0
    assert ok_audit["unsupported_claims"] == []
    assert ok_audit["verified_claims_count"] >= 5

    # 2. Hallucinated answer with fabricated figures -> intercepted!
    hallucinated = (
        "For SKU-FAKE-777, EuroOptics charges $999.00 per unit with a 47.5% penalty and 99 calendar days lead time."
    )
    bad_audit = hallucination_guard.verify_answer_grounding(hallucinated, source_snippets)
    assert bad_audit["is_grounded"] is False
    assert bad_audit["faithfulness_score"] == 0.0
    assert len(bad_audit["unsupported_claims"]) >= 4


def test_adversarial_hallucination_traps_abstain_with_zero_hallucinations():
    """
    Executes all 6 adversarial unanswerable traps end-to-end through the full RAG pipeline.
    Every single trap must safely abstain ('Clause Not Specified') with 0% hallucination rate.
    """
    for trap in ADVERSARIAL_HALLUCINATION_TRAPS:
        res = rag_service.answer_query(trap["query"], top_k=5, retrieval_mode="hybrid")
        gv = res["grounding_verification"]
        assert gv["abstained"] is True, f"Trap was NOT abstained: {trap['query']}"
        assert gv["is_grounded"] is True
        assert gv["unsupported_claims"] == []
        assert "Clause Not Specified" in res["answer"]
        assert res["citations"] == []


def test_answerable_queries_pass_100_percent_grounding_audit():
    """
    Verifies real contract queries across the 6 multi-page PDFs answer accurately
    with 100% faithfulness and zero unsupported claims.
    """
    for case in GOLDEN_RAG_BENCHMARK[:5]:
        res = rag_service.answer_query(case["query"], top_k=5, retrieval_mode="hybrid")
        gv = res["grounding_verification"]
        assert gv["abstained"] is False, f"Valid query was wrongly abstained: {case['query']}"
        assert gv["is_grounded"] is True
        assert gv["faithfulness_score"] == 1.0
        assert gv["unsupported_claims"] == []
        assert len(res["citations"]) >= 1


def test_full_hallucination_audit_report():
    report = benchmark_suite.evaluate_hallucination_guard()
    assert report["hallucination_rate_pct"] == 0.0
    assert report["avg_faithfulness_score_pct"] == 100.0
    assert report["adversarial_abstention_accuracy_pct"] == 100.0
    assert report["synthetic_fabrication_interception"]["passed"] is True


def test_all_five_ai_forecasting_models_head_to_head():
    """
    Tests 5 distinct AI forecasting model families on a deterministic seasonal synthetic dataset:
      - Ridge L2 Autoregressive
      - Facebook Prophet (Fourier Seasonality)
      - Random Forest (Bagged Tree Quantiles)
      - XGBoost (Depth-Wise Regularized GBDT)
      - LightGBM Quantile (Leaf-Wise Pinball GBDT)
    """
    rng = np.random.default_rng(42)
    days = 100
    start = date.today() - timedelta(days=days)
    dates = [start + timedelta(days=i) for i in range(days)]
    # Clear weekly seasonality + mild upward trend + low noise
    y = np.array([
        max(5, round(30 + 0.08 * i + 6 * np.sin(2 * np.pi * (i % 7) / 7.0) + rng.normal(0, 1.8)))
        for i in range(days)
    ], dtype=float)
    df = pd.DataFrame({"sales_date": dates, "quantity_sold": y})

    test_days = 14
    train_df = df.iloc[:-test_days].copy()
    test_df = df.iloc[-test_days:].copy()
    y_true = test_df["quantity_sold"].values
    test_dates = pd.to_datetime(test_df["sales_date"]).dt.strftime("%Y-%m-%d")

    models = [
        ("Ridge", RidgeLagForecaster),
        ("Prophet", ProphetForecaster),
        ("RandomForest", RandomForestForecaster),
        ("XGBoost", XGBoostForecaster),
        ("LightGBM", LightGBMForecaster),
    ]

    for name, cls in models:
        m = cls()
        pred_df = m.fit_predict(train_df, horizon_days=test_days)
        matched = pred_df[pred_df["ds"].isin(test_dates)]
        assert len(matched) == test_days, f"{name} did not return {test_days} forecast rows"
        assert (matched["yhat"] >= 0).all(), f"{name} produced negative predictions"
        assert (matched["yhat_upper"] >= matched["yhat"]).all(), f"{name} upper bound < point forecast"
        metrics = ForecastEvaluator.calculate_metrics(y_true, matched["yhat"].values)
        assert metrics["mape"] < 25.0, f"{name} MAPE too high on clean seasonal data: {metrics['mape']}%"
