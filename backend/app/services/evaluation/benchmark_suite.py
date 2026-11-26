from typing import List, Dict, Any, Optional
import time
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from app.services.rag.retrieval import vector_store
from app.services.rag.generation import rag_service
from app.services.rag.hallucination_guard import hallucination_guard
from app.services.forecasting.evaluator import ForecastEvaluator
from app.services.forecasting.prophet_model import ProphetForecaster
from app.services.forecasting.lightgbm_model import LightGBMForecaster
from app.services.forecasting.multi_model_forecasters import (
    XGBoostForecaster,
    RandomForestForecaster,
    RidgeLagForecaster,
)
from app.db.models.product import Product
from app.db.models.sales_history import SalesHistory


# Golden Legal & Supply Chain Retrieval Evaluation Dataset (Multi-PDF Corpus)
GOLDEN_RAG_BENCHMARK = [
    {
        "query": "What is the expedited 10-day turnaround rush surcharge for SKU-MCU-32B?",
        "expected_supplier_substr": "Apex",
        "expected_terms": ["20%", "10-day", "expedited"],
    },
    {
        "query": "Section 7.2 liquidated damages cap and weekly late penalty for Apex Microelectronics",
        "expected_supplier_substr": "Apex",
        "expected_terms": ["2.0%", "12%", "liquidated"],
    },
    {
        "query": "2026 Q2 addendum tiered volume pricing discount above 1,500 units for SKU-MCU-32B",
        "expected_supplier_substr": "Apex",
        "expected_terms": ["6%", "1,500", "addendum"],
    },
    {
        "query": "Malacca Strait maritime congestion lead time extension for SKU-LENS-4K",
        "expected_supplier_substr": "Pacific",
        "expected_terms": ["35", "42", "malacca"],
    },
    {
        "query": "What is the 12.5% logistics energy surcharge effective March 1 2026?",
        "expected_supplier_substr": "Pacific",
        "expected_terms": ["12.5%", "surcharge", "march"],
    },
    {
        "query": "Nordic Silicon FOB Oslo guaranteed lead time and 1.5% weekly late delivery penalty",
        "expected_supplier_substr": "Nordic",
        "expected_terms": ["14", "1.5%", "oslo"],
    },
    {
        "query": "30-day revolving consignment warehouse buffer and 5% batch volume discount",
        "expected_supplier_substr": "Nordic",
        "expected_terms": ["30-day", "5%", "1,000"],
    },
    {
        "query": "ISO 9001:2015 and IP67 waterproof polycarbonate enclosure SKU-ENC-IP67 overnight dispatch",
        "expected_supplier_substr": "Titan",
        "expected_terms": ["ip67", "iso 9001", "overnight"],
    },
    {
        "query": "EuroOptics secondary supplier ISO Class 5 cleanroom 0.02% optical defect tolerance for SKU-LENS-4K",
        "expected_supplier_substr": "EuroOptics",
        "expected_terms": ["iso class 5", "0.02%", "21.40"],
    },
    {
        "query": "Wafer allocation shortage exceeding 15% pro-rata force majeure clause",
        "expected_supplier_substr": "Apex",
        "expected_terms": ["15%", "pro-rata", "force majeure"],
    },
]

# Adversarial Hallucination Traps (Must ABSTAIN — zero fabricated numbers allowed!)
ADVERSARIAL_HALLUCINATION_TRAPS = [
    {
        "query": "What is Quantum Chips Inc.'s 45% penalty clause for SKU-QUANTUM-99?",
        "trap_type": "non_existent_sku_and_vendor",
    },
    {
        "query": "What is the exact unit price and MOQ for SKU-FAKE-9999?",
        "trap_type": "non_existent_sku",
    },
    {
        "query": "What is Apple Inc.'s Q4 iPhone stock price forecast for 2027?",
        "trap_type": "out_of_domain",
    },
    {
        "query": "What is Pacific Optics' carbon emission tax rate in Brazil?",
        "trap_type": "fabricated_clause_known_vendor",
    },
    {
        "query": "Does Titan Polymers offer a 60-month aerospace radiation warranty?",
        "trap_type": "fabricated_numeric_warranty",
    },
    {
        "query": "What is the Bitcoin payment discount in Nordic Silicon's contract?",
        "trap_type": "fabricated_payment_term",
    },
]


class AIBenchmarkSuite:
    """
    Comprehensive Empirical AI Evaluation & Anti-Hallucination Audit Engine:
      1. RAG Retrieval Ablation: Dense HNSW vs. Sparse BM25 vs. Hybrid RRF + Cross-Reranker
      2. Adversarial Hallucination & Faithfulness Audit: 10 Answerable + 6 Unanswerable Traps + Synthetic Injection
      3. Multi-Model Forecasting Leaderboard: 7 Distinct AI Models on 14-Day Holdout Backtesting
    """

    @staticmethod
    def evaluate_rag_retrieval(
        benchmark_cases: Optional[List[Dict[str, Any]]] = None,
        top_k: int = 3
    ) -> Dict[str, Any]:
        cases = benchmark_cases or GOLDEN_RAG_BENCHMARK
        modes = ["dense", "bm25", "hybrid"]
        summary_by_mode: Dict[str, Any] = {}
        per_query_comparison: List[Dict[str, Any]] = []

        for mode in modes:
            hits_at_1 = 0
            hits_at_k = 0
            reciprocal_ranks: List[float] = []
            precisions_at_k: List[float] = []
            latencies_ms: List[float] = []

            for case in cases:
                t0 = time.perf_counter()
                results = vector_store.search(case["query"], top_k=top_k, mode=mode)
                elapsed_ms = (time.perf_counter() - t0) * 1000.0
                latencies_ms.append(elapsed_ms)

                exp_sup = case["expected_supplier_substr"].lower()
                exp_terms = [t.lower() for t in case["expected_terms"]]

                first_hit_rank: Optional[int] = None
                relevant_count = 0

                for rank, res in enumerate(results, start=1):
                    combined = (
                        f"{res.get('supplier_name', '')} {res.get('doc_title', '')} {res.get('content', '')}"
                    ).lower()
                    supplier_match = exp_sup in combined
                    term_matches = sum(1 for t in exp_terms if t in combined)
                    is_relevant = supplier_match and term_matches >= 1

                    if is_relevant:
                        relevant_count += 1
                        if first_hit_rank is None:
                            first_hit_rank = rank

                if first_hit_rank == 1:
                    hits_at_1 += 1
                if first_hit_rank is not None and first_hit_rank <= top_k:
                    hits_at_k += 1
                    reciprocal_ranks.append(1.0 / first_hit_rank)
                else:
                    reciprocal_ranks.append(0.0)

                precisions_at_k.append(relevant_count / max(1, top_k))

            n = max(1, len(cases))
            summary_by_mode[mode] = {
                "hit_at_1_pct": round((hits_at_1 / n) * 100.0, 1),
                f"hit_at_{top_k}_pct": round((hits_at_k / n) * 100.0, 1),
                "mrr": round(float(np.mean(reciprocal_ranks)), 4),
                f"precision_at_{top_k}": round(float(np.mean(precisions_at_k)), 4),
                "avg_latency_ms": round(float(np.mean(latencies_ms)), 2),
                "queries_evaluated": len(cases),
            }

        for case in cases[:5]:
            dense_top = vector_store.search(case["query"], top_k=1, mode="dense")
            hybrid_top = vector_store.search(case["query"], top_k=1, mode="hybrid")
            per_query_comparison.append({
                "query": case["query"],
                "expected_supplier": case["expected_supplier_substr"],
                "dense_top1_doc": dense_top[0]["doc_title"] if dense_top else "None",
                "dense_score": dense_top[0]["score"] if dense_top else 0.0,
                "hybrid_top1_doc": hybrid_top[0]["doc_title"] if hybrid_top else "None",
                "hybrid_score": hybrid_top[0]["score"] if hybrid_top else 0.0,
                "hybrid_bm25_score": hybrid_top[0].get("bm25_score", 0.0) if hybrid_top else 0.0,
            })

        return {
            "benchmark_name": "Multi-PDF Legal Contract Retrieval Ablation",
            "corpus_chunks_indexed": vector_store._bm25.size,
            "modes": summary_by_mode,
            "hybrid_vs_dense_mrr_gain": round(
                summary_by_mode["hybrid"]["mrr"] - summary_by_mode["dense"]["mrr"], 4
            ),
            "sample_queries": per_query_comparison,
        }

    @staticmethod
    def evaluate_hallucination_guard() -> Dict[str, Any]:
        """
        Adversarial Anti-Hallucination & Faithfulness Audit:
          - Tests 10 answerable contract queries for 100% claim grounding & faithfulness
          - Tests 6 adversarial trap queries for safe abstention ('Clause Not Specified')
          - Runs a synthetic fabrication injection test verifying numeric hallucination interception
        """
        answerable_grounded = 0
        answerable_faithfulness_scores: List[float] = []
        hallucinated_responses = 0

        for case in GOLDEN_RAG_BENCHMARK:
            res = rag_service.answer_query(case["query"], top_k=5, retrieval_mode="hybrid")
            gv = res.get("grounding_verification", {})
            is_ok = bool(gv.get("is_grounded")) and not bool(gv.get("abstained"))
            if is_ok:
                answerable_grounded += 1
            if not gv.get("is_grounded", True) or len(gv.get("unsupported_claims", [])) > 0:
                hallucinated_responses += 1
            answerable_faithfulness_scores.append(float(gv.get("faithfulness_score", 1.0)))

        traps_safely_abstained = 0
        trap_details: List[Dict[str, Any]] = []
        for trap in ADVERSARIAL_HALLUCINATION_TRAPS:
            res = rag_service.answer_query(trap["query"], top_k=5, retrieval_mode="hybrid")
            gv = res.get("grounding_verification", {})
            abstained = bool(gv.get("abstained"))
            if abstained:
                traps_safely_abstained += 1
            else:
                hallucinated_responses += 1
            trap_details.append({
                "query": trap["query"],
                "trap_type": trap["trap_type"],
                "safely_abstained": abstained,
                "reason": gv.get("abstention_reason") or "Answered without abstention",
            })

        # Synthetic LLM hallucination injection verification
        sample_chunks = vector_store.search("SKU-LENS-4K EuroOptics price", top_k=2, mode="hybrid")
        fabricated_llm_output = (
            "EuroOptics charges $999.00 per unit for SKU-LENS-4K with a 47.5% penalty and 99 calendar days lead time."
        )
        synthetic_audit = hallucination_guard.verify_answer_grounding(fabricated_llm_output, sample_chunks)
        synthetic_intercepted = (not synthetic_audit["is_grounded"]) and len(synthetic_audit["unsupported_claims"]) >= 2

        total_queries = len(GOLDEN_RAG_BENCHMARK) + len(ADVERSARIAL_HALLUCINATION_TRAPS)
        hallucination_rate_pct = round((hallucinated_responses / max(1, total_queries)) * 100.0, 2)

        return {
            "audit_name": "Zero-Hallucination & Adversarial Faithfulness Audit",
            "total_queries_audited": total_queries,
            "hallucination_rate_pct": hallucination_rate_pct,
            "answerable_grounding_accuracy_pct": round(
                (answerable_grounded / max(1, len(GOLDEN_RAG_BENCHMARK))) * 100.0, 1
            ),
            "avg_faithfulness_score_pct": round(float(np.mean(answerable_faithfulness_scores)) * 100.0, 1),
            "adversarial_abstention_accuracy_pct": round(
                (traps_safely_abstained / max(1, len(ADVERSARIAL_HALLUCINATION_TRAPS))) * 100.0, 1
            ),
            "synthetic_fabrication_interception": {
                "passed": synthetic_intercepted,
                "detected_fabricated_claims": synthetic_audit["unsupported_claims"],
                "faithfulness_score_on_fabrication": synthetic_audit["faithfulness_score"],
            },
            "adversarial_traps": trap_details,
        }

    @staticmethod
    def _eval_model_on_split(
        forecaster_cls,
        train_df: pd.DataFrame,
        test_df: pd.DataFrame,
        test_days: int,
    ) -> Dict[str, Any]:
        y_true = test_df["quantity_sold"].values.astype(float)
        test_dates = pd.to_datetime(test_df["sales_date"]).dt.strftime("%Y-%m-%d")

        t0 = time.perf_counter()
        model = forecaster_cls()
        pred_df = model.fit_predict(
            train_df, horizon_days=test_days, date_col="sales_date", target_col="quantity_sold"
        )
        latency_ms = round((time.perf_counter() - t0) * 1000.0, 1)

        matched = pred_df[pred_df["ds"].isin(test_dates)]
        if len(matched) == len(y_true):
            y_hat = matched["yhat"].values.astype(float)
            y_upper = matched["yhat_upper"].values.astype(float)
            metrics = ForecastEvaluator.calculate_metrics(y_true, y_hat)
            p90_cov = round(float(np.mean(y_true <= y_upper) * 100.0), 1)
        else:
            y_hat = np.full(len(y_true), float(train_df["quantity_sold"].tail(7).mean()))
            y_upper = y_hat * 1.25
            metrics = ForecastEvaluator.calculate_metrics(y_true, y_hat)
            p90_cov = round(float(np.mean(y_true <= y_upper) * 100.0), 1)

        return {
            **metrics,
            "p90_coverage_pct": p90_cov,
            "latency_ms": latency_ms,
            "_yhat": y_hat,
            "_yupper": y_upper,
        }

    @staticmethod
    def evaluate_forecasting_models(db: Session, test_days: int = 14) -> Dict[str, Any]:
        """
        Head-to-Head Multi-Model AI Backtest across all active SKUs comparing 7 distinct models:
          1. Naive 7-Day Moving Average (Statistical Baseline)
          2. Ridge Autoregressive Lag Model (L2 Regularized Linear ML)
          3. Facebook Prophet (Bayesian Fourier Seasonality)
          4. Random Forest Ensemble (Bagged Trees + Empirical Tree Quantiles)
          5. XGBoost (Depth-Wise Regularized GBDT)
          6. LightGBM Quantile (Leaf-Wise GBDT + Pinball Loss)
          7. Stacked Meta-Ensemble (LightGBM + XGBoost + Prophet)
        """
        products = db.query(Product).all()
        model_keys = [
            "naive_ma7",
            "ridge_lag",
            "prophet",
            "random_forest",
            "xgboost",
            "lightgbm_quantile",
            "stacked_ensemble",
        ]
        model_labels = {
            "naive_ma7": "Naive 7-Day Moving Average (Baseline)",
            "ridge_lag": "Ridge L2 Autoregressive ML",
            "prophet": "Facebook Prophet (Fourier Seasonality)",
            "random_forest": "Random Forest (Bagged Tree Quantiles)",
            "xgboost": "XGBoost (Depth-Wise Regularized GBDT)",
            "lightgbm_quantile": "LightGBM Quantile (Leaf-Wise Pinball GBDT)",
            "stacked_ensemble": "Stacked Ensemble (LGBM + XGB + Prophet)",
        }

        agg: Dict[str, Dict[str, List[float]]] = {
            k: {"mape": [], "rmse": [], "mae": [], "wape": [], "p90": [], "latency": []}
            for k in model_keys
        }
        sku_results: List[Dict[str, Any]] = []

        for prod in products:
            sales = (
                db.query(SalesHistory)
                .filter(SalesHistory.product_id == prod.id)
                .order_by(SalesHistory.sales_date.asc())
                .all()
            )
            if len(sales) <= test_days + 14:
                continue

            df = pd.DataFrame([
                {"sales_date": s.sales_date, "quantity_sold": s.quantity_sold}
                for s in sales
            ])
            train_df = df.iloc[:-test_days].copy()
            test_df = df.iloc[-test_days:].copy()
            y_true = test_df["quantity_sold"].values.astype(float)

            # 1. Naive MA-7 Baseline
            t0 = time.perf_counter()
            ma_val = float(train_df["quantity_sold"].tail(7).mean())
            ma_std = float(train_df["quantity_sold"].tail(14).std() or 1.0)
            naive_pred = np.full(len(y_true), ma_val)
            naive_upper = naive_pred + 1.645 * ma_std
            naive_res = {
                **ForecastEvaluator.calculate_metrics(y_true, naive_pred),
                "p90_coverage_pct": round(float(np.mean(y_true <= naive_upper) * 100.0), 1),
                "latency_ms": round((time.perf_counter() - t0) * 1000.0, 2),
            }

            # 2-6. ML & Statistical Models
            ridge_res = AIBenchmarkSuite._eval_model_on_split(RidgeLagForecaster, train_df, test_df, test_days)
            prophet_res = AIBenchmarkSuite._eval_model_on_split(ProphetForecaster, train_df, test_df, test_days)
            rf_res = AIBenchmarkSuite._eval_model_on_split(RandomForestForecaster, train_df, test_df, test_days)
            xgb_res = AIBenchmarkSuite._eval_model_on_split(XGBoostForecaster, train_df, test_df, test_days)
            lgbm_res = AIBenchmarkSuite._eval_model_on_split(LightGBMForecaster, train_df, test_df, test_days)

            # 7. Stacked Ensemble (40% LightGBM + 35% XGBoost + 25% Prophet)
            ens_yhat = 0.40 * lgbm_res["_yhat"] + 0.35 * xgb_res["_yhat"] + 0.25 * prophet_res["_yhat"]
            ens_yupper = np.maximum.reduce([lgbm_res["_yupper"], xgb_res["_yupper"], prophet_res["_yupper"]])
            ens_res = {
                **ForecastEvaluator.calculate_metrics(y_true, ens_yhat),
                "p90_coverage_pct": round(float(np.mean(y_true <= ens_yupper) * 100.0), 1),
                "latency_ms": round(lgbm_res["latency_ms"] + xgb_res["latency_ms"] + prophet_res["latency_ms"], 1),
            }

            run_map = {
                "naive_ma7": naive_res,
                "ridge_lag": ridge_res,
                "prophet": prophet_res,
                "random_forest": rf_res,
                "xgboost": xgb_res,
                "lightgbm_quantile": lgbm_res,
                "stacked_ensemble": ens_res,
            }

            clean_sku_row: Dict[str, Any] = {
                "sku": prod.sku,
                "product_name": prod.name,
                "holdout_days": test_days,
            }
            for k, r in run_map.items():
                agg[k]["mape"].append(r["mape"])
                agg[k]["rmse"].append(r["rmse"])
                agg[k]["mae"].append(r["mae"])
                agg[k]["wape"].append(r["wape"])
                agg[k]["p90"].append(r["p90_coverage_pct"])
                agg[k]["latency"].append(r["latency_ms"])
                clean_sku_row[k] = {
                    kk: vv for kk, vv in r.items() if not kk.startswith("_")
                }

            sku_results.append(clean_sku_row)

        aggregate_comparison: Dict[str, Any] = {}
        leaderboard: List[Dict[str, Any]] = []

        for k in model_keys:
            row = {
                "model_key": k,
                "model_name": model_labels[k],
                "avg_mape": round(float(np.mean(agg[k]["mape"])), 2) if agg[k]["mape"] else 0.0,
                "avg_rmse": round(float(np.mean(agg[k]["rmse"])), 2) if agg[k]["rmse"] else 0.0,
                "avg_mae": round(float(np.mean(agg[k]["mae"])), 2) if agg[k]["mae"] else 0.0,
                "avg_wape": round(float(np.mean(agg[k]["wape"])), 2) if agg[k]["wape"] else 0.0,
                "avg_p90_coverage_pct": round(float(np.mean(agg[k]["p90"])), 1) if agg[k]["p90"] else 0.0,
                "avg_latency_ms": round(float(np.mean(agg[k]["latency"])), 1) if agg[k]["latency"] else 0.0,
            }
            aggregate_comparison[k] = row
            leaderboard.append(row)

        leaderboard.sort(key=lambda x: (x["avg_mape"], x["avg_rmse"]))
        best_model = leaderboard[0]["model_name"] if leaderboard else "N/A"

        return {
            "benchmark_name": f"7-Model AI Forecasting Holdout Backtest ({test_days}-Day Horizon)",
            "skus_evaluated": len(sku_results),
            "models_tested": len(model_keys),
            "best_model_by_mape": best_model,
            "leaderboard": leaderboard,
            "aggregate_comparison": aggregate_comparison,
            "per_sku": sku_results,
        }


benchmark_suite = AIBenchmarkSuite()
