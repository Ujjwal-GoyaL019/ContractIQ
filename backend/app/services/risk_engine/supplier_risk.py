from typing import Dict, Any, List, Optional
from app.services.rag.retrieval import vector_store


class SupplierRiskEvaluator:
    """
    Computes supplier reliability and disruption risk scores by blending
    historical order delivery logs with document-extracted risk clauses.
    """

    @staticmethod
    def calculate_supplier_risk(
        reliability_score: float, # 0.0 to 1.0 (on-time rate)
        quality_score: float,     # 0.0 to 1.0 (defect-free rate)
        base_lead_time_days: int,
        country: str,
        supplier_id: Optional[str] = None,
        supplier_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        reasons = []
        
        # 1. Performance-based risk component (0-50 pts)
        late_penalty = (1.0 - reliability_score) * 40.0
        quality_penalty = (1.0 - quality_score) * 30.0
        base_score = late_penalty + quality_penalty

        if reliability_score < 0.85:
            reasons.append(f"Low on-time fulfillment rate ({round(reliability_score*100, 1)}%)")
        if quality_score < 0.90:
            reasons.append(f"Elevated defect / inspection rejection rate ({round((1-quality_score)*100, 1)}%)")

        # 2. Lead-time vulnerability (0-15 pts)
        if base_lead_time_days >= 45:
            base_score += 15.0
            reasons.append(f"Extended supplier lead time ({base_lead_time_days} days)")
        elif base_lead_time_days >= 25:
            base_score += 8.0
            reasons.append(f"Moderate lead time exposure ({base_lead_time_days} days)")

        # 3. Document risk clause analysis via RAG
        doc_risk_score = 0.0
        if supplier_id:
            # Query vector store for high risk terms in supplier's docs
            risk_hits = vector_store.search(
                query="force majeure price increase delivery delay component shortage breach",
                top_k=3,
                supplier_id=supplier_id
            )
            for hit in risk_hits:
                content_lower = hit["content"].lower()
                if "force majeure" in content_lower or "unforeseen event" in content_lower:
                    doc_risk_score += 12.0
                    reasons.append("Active force majeure / allocation clause identified in contract")
                elif "price increase" in content_lower or "surcharge" in content_lower:
                    doc_risk_score += 8.0
                    reasons.append("Notified price increase / freight surcharge in agreement")
                elif "delay" in content_lower or "lead time extension" in content_lower:
                    doc_risk_score += 10.0
                    reasons.append("Notice of lead time extensions or capacity constraints")

        total_risk = min(100.0, max(0.0, base_score + doc_risk_score))

        if not reasons:
            reasons.append("Optimal supplier fulfillment track record and terms")

        return {
            "supplier_disruption_risk": round(float(total_risk), 1),
            "risk_reasons": list(set(reasons)),
            "is_high_risk": total_risk >= 50.0
        }


supplier_risk_evaluator = SupplierRiskEvaluator()
