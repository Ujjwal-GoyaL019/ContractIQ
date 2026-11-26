from typing import List, Dict, Any, Optional, Tuple
import re


# Patterns for high-stakes factual claims that must NEVER be fabricated
SKU_PATTERN = re.compile(r"\bSKU-[A-Z0-9-]+\b", re.IGNORECASE)
PCT_PATTERN = re.compile(r"\b\d+(?:\.\d+)?%")
CURRENCY_PATTERN = re.compile(r"\$\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?")
DURATION_PATTERN = re.compile(
    r"\b\d+(?:\s*[-–]\s*\d+)?\s*(?:calendar\s+days?|business\s+days?|days?|weeks?|months?|hours?)\b",
    re.IGNORECASE,
)
ISO_PATTERN = re.compile(r"\bISO\s*(?:Class\s*)?\d+(?::\d+)?\b", re.IGNORECASE)
CLAUSE_PATTERN = re.compile(r"\b(?:Section|Clause|Article)\s+\d+(?:\.\d+)*\b", re.IGNORECASE)
DPPM_PATTERN = re.compile(r"\b\d+\s*DPPM\b", re.IGNORECASE)

# Known catalog entities / suppliers for detecting out-of-catalog fabrications
STOP_PROPER = {
    "What", "Which", "Where", "When", "How", "Does", "Is", "Are", "Can", "Will",
    "Compare", "Explain", "List", "Show", "Give", "Tell", "Section", "Clause",
    "Article", "Standard", "Minimum", "Order", "Quantity", "Lead", "Time",
    "Master", "Supply", "Agreement", "Notice", "Addendum", "Cleanroom", "Force",
    "Majeure", "Payment", "Terms", "Penalty", "Discount", "Surcharge", "March",
    "April", "January", "February", "May", "June", "July", "August", "September",
    "October", "November", "December", "FOB", "SLA", "MOQ", "SKU", "ISO", "IP67",
    "USD", "OTD", "OTIF", "DPPM", "BLE", "MCU", "SoC", "Q1", "Q2", "Q3", "Q4",
}

OUT_OF_DOMAIN_MARKERS = {
    "bitcoin", "crypto", "ethereum", "iphone", "stock price", "weather",
    "recipe", "football", "cricket", "movie", "celebrity", "president",
    "radiation", "aerospace", "carbon emission", "tax rate in brazil",
}


def extract_factual_claims(text: str) -> List[str]:
    """
    Extracts concrete verifiable claims (SKUs, percentages, currency amounts,
    durations, ISO standards, section IDs, DPPM metrics) from text.
    """
    if not text:
        return []
    claims = set()
    for pat in (
        SKU_PATTERN,
        PCT_PATTERN,
        CURRENCY_PATTERN,
        DURATION_PATTERN,
        ISO_PATTERN,
        CLAUSE_PATTERN,
        DPPM_PATTERN,
    ):
        for match in pat.findall(text):
            normalized = re.sub(r"\s+", " ", match.strip())
            claims.add(normalized)
    return sorted(claims)


def _normalize_for_match(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).replace("–", "-").replace(",", "")


def _claim_present_in_source(claim: str, source_norm: str) -> bool:
    """
    Checks whether a specific numeric/entity claim is grounded in the retrieved source context.
    Handles minor formatting variations like '$21.40' vs '$21.4', '14-day' vs '14 days', '2.0%' vs '2%'.
    """
    c_norm = _normalize_for_match(claim)
    if c_norm in source_norm:
        return True

    # Handle plural/singular or hyphenated duration variants (e.g., '14 days' vs '14-day')
    if "day" in c_norm or "month" in c_norm or "week" in c_norm or "hour" in c_norm:
        nums = re.findall(r"\d+", c_norm)
        unit_match = re.search(r"(day|week|month|hour)", c_norm)
        if nums and unit_match:
            unit = unit_match.group(1)
            # Check if the exact number appears within 25 chars of that unit in source
            for num in nums:
                pattern = rf"\b{re.escape(num)}\b(?:\s*[-a-z0-9]{{0,20}})?\b{unit}s?\b"
                if re.search(pattern, source_norm):
                    return True

    # Handle decimal percentage equivalence: '2.0%' == '2%'
    if c_norm.endswith("%"):
        try:
            val = float(c_norm[:-1])
            alt = f"{int(val)}%" if val.is_integer() else f"{val}%"
            if alt in source_norm:
                return True
        except ValueError:
            pass

    # Handle Section/Clause/Article equivalence: 'section 7.2' matches standalone '7.2' numbering in PDF
    if re.match(r"^(?:section|clause|article)\s+\d+(?:\.\d+)*$", c_norm):
        sec_num = c_norm.split()[-1]
        if re.search(rf"\b{re.escape(sec_num)}\b", source_norm):
            return True

    # Handle currency equivalence: '$6.80' == '$6.8'
    if c_norm.startswith("$"):
        try:
            val = float(c_norm[1:])
            if f"${val:.2f}" in source_norm or f"${val:g}" in source_norm:
                return True
        except ValueError:
            pass

    return False


class HallucinationGuard:
    """
    Three-stage Deterministic Anti-Hallucination Shield for Legal Contract RAG:
      1. Pre-Generation Abstention Gate: Blocks answering when queried SKUs, entities,
         or topics are unsupported by the retrieved contract corpus.
      2. Zero-Hallucination Extractive Synthesizer: Constructs query-focused answers
         verbatim from retrieved PDF sentences with exact [Title, Page] citations.
      3. Post-Generation Factuality Auditor: Extracts every number, SKU, percentage,
         dollar value, ISO spec, and duration from any LLM output and verifies it
         against the retrieved context, rejecting/correcting unsupported fabrications.
    """

    def __init__(
        self,
        min_dense_score: float = 0.48,
        min_bm25_score: float = 2.0,
    ):
        self.min_dense_score = min_dense_score
        self.min_bm25_score = min_bm25_score

    def evaluate_retrieval_confidence(
        self,
        query: str,
        snippets: List[Dict[str, Any]],
    ) -> Tuple[bool, Optional[str]]:
        """
        Returns (should_answer, abstention_reason).
        If should_answer is False, the pipeline MUST abstain rather than risk hallucination.
        """
        if not snippets:
            return False, "No indexed contract documents matched your query."

        q_lower = query.lower()
        combined_source = " ".join(
            f"{s.get('doc_title', '')} {s.get('supplier_name', '')} {s.get('content', '')}"
            for s in snippets
        )
        source_norm = _normalize_for_match(combined_source)

        # 1. Explicit SKU Verification: if user asks about SKU-XXXX, that exact SKU must exist in context
        queried_skus = SKU_PATTERN.findall(query)
        for sku in queried_skus:
            if sku.lower() not in source_norm:
                return (
                    False,
                    f"Clause Not Specified: The queried SKU '{sku.upper()}' does not appear in any indexed supplier contract or notice.",
                )

        # 2. Out-of-domain / fabricated clause guard (e.g., crypto, stock prices, radiation warranty, carbon tax)
        for marker in OUT_OF_DOMAIN_MARKERS:
            if marker in q_lower and marker not in source_norm:
                return (
                    False,
                    f"Clause Not Specified: No indexed supplier agreement contains provisions regarding '{marker}'.",
                )

        # 3. Unknown explicit numeric/percentage/warranty trap check
        # e.g., asking "Does Titan offer a 60-month warranty?" or "45% penalty" when number isn't in context
        queried_specifics = (
            PCT_PATTERN.findall(query)
            + CURRENCY_PATTERN.findall(query)
            + re.findall(r"\b\d+\s*[- ]?(?:month|year)\b", query, re.IGNORECASE)
        )
        if queried_specifics:
            unmatched_specifics = [
                sp for sp in queried_specifics if not _claim_present_in_source(sp, source_norm)
            ]
            # If user asserts specific numbers that appear nowhere in the retrieved contracts, refuse to confirm
            if len(unmatched_specifics) == len(queried_specifics):
                return (
                    False,
                    f"Clause Not Specified: Indexed supplier agreements do not contain the queried terms ({', '.join(unmatched_specifics)}).",
                )

        # 4. Unknown Named Entity Check (e.g. "Quantum Chips", "Apple Inc.")
        proper_tokens = [
            w for w in re.findall(r"\b[A-Z][a-z]{2,}\b", query)
            if w not in STOP_PROPER
        ]
        if proper_tokens:
            unmatched_entities = [w for w in proper_tokens if w.lower() not in source_norm]
            # If user names an entity completely absent from all top chunks, abstain
            if len(unmatched_entities) >= 1 and len(unmatched_entities) == len(proper_tokens):
                # Check if any known catalog words appear; if not, it's an unknown company/topic
                return (
                    False,
                    f"Clause Not Specified: No indexed supplier contract references '{' '.join(unmatched_entities)}'.",
                )

        # 5. Quantitative Score Floor: prevent weak low-similarity chunks from passing
        top_dense = max((float(s.get("dense_score", s.get("score", 0.0))) for s in snippets), default=0.0)
        top_bm25 = max((float(s.get("bm25_score", 0.0)) for s in snippets), default=0.0)

        if top_dense < self.min_dense_score and top_bm25 < self.min_bm25_score:
            return (
                False,
                f"Insufficient Contract Evidence: Retrieval confidence below grounding threshold "
                f"(dense={top_dense:.2f} < {self.min_dense_score}, bm25={top_bm25:.2f} < {self.min_bm25_score}).",
            )

        return True, None

    def build_abstention_response(self, query: str, reason: str) -> Dict[str, Any]:
        answer = (
            f"### Clause Not Specified (Abstained to Prevent Hallucination)\n\n"
            f"- **Query**: *\"{query}\"*\n"
            f"- **Verification Status**: **Abstained (Insufficient Contract Evidence)**\n"
            f"- **Reason**: {reason}\n\n"
            f"ContractIQ's anti-hallucination guardrail strictly refuses to speculate on terms, SKUs, suppliers, "
            f"or financial penalties not explicitly documented in the indexed PDF agreements."
        )
        return {
            "answer": answer,
            "citations": [],
            "risk_flags_detected": [],
            "suggested_followups": [
                "Which suppliers have active force majeure or lead-time risk notices?",
                "What are Apex Microelectronics' Section 7.2 liquidated damages?",
                "Compare SKU-LENS-4K terms between Pacific Optics and EuroOptics GmbH."
            ],
            "grounding_verification": {
                "is_grounded": True,
                "abstained": True,
                "faithfulness_score": 1.0,
                "verified_claims_count": 0,
                "unsupported_claims": [],
                "abstention_reason": reason,
                "verification_method": "pre_generation_abstention_gate",
            },
        }

    def synthesize_extractive_grounded_answer(
        self,
        query: str,
        snippets: List[Dict[str, Any]],
    ) -> str:
        """
        Zero-hallucination extractive answer builder: extracts the highest-overlap verbatim
        sentences from retrieved PDF chunks with exact [Document Title, Page X] citations.
        Introduces zero ungrounded numbers or fabricated terms.
        """
        q_words = set(re.findall(r"[a-z0-9.%-]+", query.lower()))
        q_words -= {"what", "which", "the", "and", "for", "with", "are", "is", "of", "in", "to", "a", "an"}

        scored_sentences: List[Tuple[float, Dict[str, Any], str]] = []
        seen_sentences = set()

        for rank, snip in enumerate(snippets[:4]):
            content = snip.get("content", "").strip()
            sentences = re.split(r"(?<=[.!?])\s+", content)
            for sent in sentences:
                s_clean = sent.strip()
                if len(s_clean) < 25 or s_clean in seen_sentences:
                    continue
                seen_sentences.add(s_clean)
                s_words = set(re.findall(r"[a-z0-9.%-]+", s_clean.lower()))
                overlap = len(q_words & s_words) / max(1, len(q_words))
                rank_bonus = 0.25 / (rank + 1)
                scored_sentences.append((overlap + rank_bonus, snip, s_clean))

        scored_sentences.sort(key=lambda x: x[0], reverse=True)
        selected = scored_sentences[:3]

        if not selected:
            top = snippets[0]
            return (
                f"### Verified Contract Extract\n\n"
                f"- **[{top.get('doc_title', 'Contract')}, Page {top.get('page_number', 1)}]** "
                f"(*{top.get('supplier_name', 'Supplier')}*): \"{top.get('content', '').strip()}\""
            )

        lines = ["### Verified Contract Findings (Grounded Extract)\n"]
        for idx, (_, snip, sent) in enumerate(selected, start=1):
            doc_title = snip.get("doc_title", "Supplier Contract")
            supplier = snip.get("supplier_name", "Supplier")
            page = snip.get("page_number", 1)
            lines.append(f"{idx}. **{doc_title}** (*{supplier}*, Page {page}):\n   > {sent}\n")

        return "\n".join(lines)

    def verify_answer_grounding(
        self,
        answer_text: str,
        snippets: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Post-generation Claim & Numeric Factuality Audit.
        Verifies every extracted numeric/entity claim in the generated answer against the
        retrieved PDF chunks. Flags any unverified claim as a hallucination.
        """
        combined_source = " ".join(
            f"{s.get('doc_title', '')} {s.get('supplier_name', '')} Page {s.get('page_number', 1)} {s.get('content', '')}"
            for s in snippets
        )
        source_norm = _normalize_for_match(combined_source)

        claims = extract_factual_claims(answer_text)
        if not claims:
            return {
                "is_grounded": True,
                "abstained": False,
                "faithfulness_score": 1.0,
                "verified_claims_count": 0,
                "unsupported_claims": [],
                "abstention_reason": None,
                "verification_method": "deterministic_claim_entity_audit",
            }

        verified: List[str] = []
        unsupported: List[str] = []

        for claim in claims:
            if _claim_present_in_source(claim, source_norm):
                verified.append(claim)
            else:
                unsupported.append(claim)

        faithfulness = len(verified) / len(claims)
        return {
            "is_grounded": len(unsupported) == 0,
            "abstained": False,
            "faithfulness_score": round(float(faithfulness), 4),
            "verified_claims_count": len(verified),
            "unsupported_claims": unsupported,
            "abstention_reason": None,
            "verification_method": "deterministic_claim_entity_audit",
        }


hallucination_guard = HallucinationGuard()
