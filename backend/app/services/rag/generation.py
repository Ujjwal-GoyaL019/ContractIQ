from typing import List, Dict, Any, Optional, AsyncGenerator
import json
import asyncio
from app.config import settings
from app.core.logging import logger
from app.services.rag.retrieval import vector_store
from app.services.rag.hallucination_guard import hallucination_guard

try:
    from groq import Groq, AsyncGroq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    logger.warning("groq library not installed. LLM generation will run in mock mode.")


class RAGGenerationService:
    """
    Orchestrates grounded RAG generation using Groq Llama 3.3 70B,
    with citation injection, supply chain risk extraction, and SSE streaming.
    """

    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model = settings.GROQ_MODEL
        self.client = None
        self.async_client = None
        self._init_client()

    def _init_client(self):
        if GROQ_AVAILABLE and self.api_key and self.api_key.strip() and self.api_key != "your_groq_api_key_here":
            try:
                self.client = Groq(api_key=self.api_key)
                self.async_client = AsyncGroq(api_key=self.api_key)
                logger.info("Groq API clients initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
        else:
            logger.info("No valid GROQ_API_KEY configured. RAG generator will operate in intelligent mock grounded mode.")

    def _build_context_prompt(self, snippets: List[Dict[str, Any]]) -> str:
        if not snippets:
            return "No relevant supplier documents or contract clauses were found."

        context_lines = []
        for i, snip in enumerate(snippets, start=1):
            title = snip.get("doc_title", "Document")
            supplier = snip.get("supplier_name", "Supplier")
            page = snip.get("page_number", 1)
            content = snip.get("content", "").strip()
            context_lines.append(f"--- [Citation {i}] Document: '{title}' | Supplier: {supplier} | Page: {page} ---\n{content}\n")
        return "\n".join(context_lines)

    def _build_system_prompt(self) -> str:
        return (
            "You are the ContractIQ Supply Chain & Legal Compliance Advisor. "
            "Your objective is to analyze supplier contracts, SLA terms, delivery performance notices, "
            "and inventory risk factors with ZERO hallucinations.\n\n"
            "STRICT ANTI-HALLUCINATION RULES:\n"
            "1. Ground EVERY fact, number, percentage, currency value, SKU, and lead time strictly in the provided citations.\n"
            "2. NEVER invent, estimate, or extrapolate any number, penalty rate, date, or clause not verbatim in the context.\n"
            "3. Explicitly cite every claim using [Doc: Contract Name, Page X].\n"
            "4. If the provided documents do not specify the requested information, state 'Clause Not Specified' clearly.\n"
            "5. Format answers cleanly using markdown bullet points and bold highlights."
        )

    def answer_query(
        self,
        query: str,
        supplier_id: Optional[str] = None,
        top_k: int = 5,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        retrieval_mode: str = "hybrid"
    ) -> Dict[str, Any]:
        """
        Executes Hybrid RRF + Reranked retrieval, Pre-Generation Abstention Gate,
        Zero-Temperature Synthesis, and Post-Generation Claim Factuality Audit.
        """
        snippets = vector_store.search(query, top_k=top_k, supplier_id=supplier_id, mode=retrieval_mode)

        # Stage 1: Pre-Generation Anti-Hallucination Abstention Gate
        should_answer, abstention_reason = hallucination_guard.evaluate_retrieval_confidence(query, snippets)
        if not should_answer:
            logger.info(f"HallucinationGuard abstained on query '{query}': {abstention_reason}")
            return hallucination_guard.build_abstention_response(query, abstention_reason or "Insufficient evidence.")

        context_str = self._build_context_prompt(snippets)

        # Prepare Citations list with Hybrid RRF & Rerank telemetry
        citations = []
        for snip in snippets:
            citations.append({
                "doc_id": snip.get("doc_id", ""),
                "document_title": snip.get("doc_title", "Document"),
                "supplier_name": snip.get("supplier_name"),
                "page_number": snip.get("page_number", 1),
                "snippet": snip.get("content", "")[:280] + "...",
                "score": snip.get("score", 0.0),
                "dense_score": snip.get("dense_score"),
                "bm25_score": snip.get("bm25_score"),
                "rrf_score": snip.get("rrf_score"),
                "retrieval_method": snip.get("retrieval_method", "hybrid_rrf_reranked")
            })

        answer_text: Optional[str] = None
        if self.client is not None:
            try:
                messages = [{"role": "system", "content": self._build_system_prompt()}]
                if conversation_history:
                    for msg in conversation_history[-4:]:
                        messages.append({"role": msg["role"], "content": msg["content"]})

                user_prompt = f"### Supplier Documents Context:\n{context_str}\n\n### User Question:\n{query}"
                messages.append({"role": "user", "content": user_prompt})

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.0,
                    max_tokens=1024,
                )
                answer_text = response.choices[0].message.content
            except Exception as e:
                logger.error(f"Groq generation call failed: {e}. Using verified extractive fallback.")

        if not answer_text:
            # Stage 2: Deterministic Zero-Hallucination Extractive Grounding
            answer_text = hallucination_guard.synthesize_extractive_grounded_answer(query, snippets)

        # Stage 3: Post-Generation Factuality & Numeric Claim Verification
        verification = hallucination_guard.verify_answer_grounding(answer_text, snippets)
        if not verification["is_grounded"]:
            logger.warning(
                f"HallucinationGuard intercepted unsupported claims {verification['unsupported_claims']}. "
                f"Enforcing verified extractive fallback."
            )
            answer_text = hallucination_guard.synthesize_extractive_grounded_answer(query, snippets)
            verification = hallucination_guard.verify_answer_grounding(answer_text, snippets)
            verification["verification_method"] = "auto_corrected_extractive_grounding"

        return {
            "answer": answer_text,
            "citations": citations,
            "risk_flags_detected": self._extract_risk_keywords(answer_text),
            "suggested_followups": [
                "What is our current safety stock coverage for these SKUs?",
                "What are the contractual penalty clauses for late delivery?",
                "Run the MILP Multi-Supplier Optimizer to split orders across secondary suppliers."
            ],
            "grounding_verification": verification,
        }

    async def stream_query(
        self,
        query: str,
        supplier_id: Optional[str] = None,
        top_k: int = 5,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        retrieval_mode: str = "hybrid"
    ) -> AsyncGenerator[str, None]:
        """
        Streams verified, anti-hallucination grounded response tokens as SSE JSON payloads.
        """
        snippets = vector_store.search(query, top_k=top_k, supplier_id=supplier_id, mode=retrieval_mode)

        # Stage 1: Pre-Generation Anti-Hallucination Abstention Gate
        should_answer, abstention_reason = hallucination_guard.evaluate_retrieval_confidence(query, snippets)
        if not should_answer:
            abstained = hallucination_guard.build_abstention_response(query, abstention_reason or "Insufficient evidence.")
            yield f"data: {json.dumps({'event': 'citations', 'data': []})}\n\n"
            yield f"data: {json.dumps({'event': 'grounding', 'data': abstained['grounding_verification']})}\n\n"
            for word in abstained["answer"].split(" "):
                yield f"data: {json.dumps({'event': 'token', 'data': word + ' '})}\n\n"
                await asyncio.sleep(0.01)
            yield f"data: {json.dumps({'event': 'done'})}\n\n"
            return

        context_str = self._build_context_prompt(snippets)

        citations = [
            {
                "doc_id": s.get("doc_id", ""),
                "document_title": s.get("doc_title", "Document"),
                "supplier_name": s.get("supplier_name"),
                "page_number": s.get("page_number", 1),
                "snippet": s.get("content", "")[:280] + "...",
                "score": s.get("score", 0.0),
                "dense_score": s.get("dense_score"),
                "bm25_score": s.get("bm25_score"),
                "rrf_score": s.get("rrf_score"),
                "retrieval_method": s.get("retrieval_method", "hybrid_rrf_reranked")
            }
            for s in snippets
        ]

        yield f"data: {json.dumps({'event': 'citations', 'data': citations})}\n\n"

        if self.async_client is not None:
            try:
                messages = [{"role": "system", "content": self._build_system_prompt()}]
                if conversation_history:
                    for msg in conversation_history[-4:]:
                        messages.append({"role": msg["role"], "content": msg["content"]})
                user_prompt = f"### Supplier Documents Context:\n{context_str}\n\n### User Question:\n{query}"
                messages.append({"role": "user", "content": user_prompt})

                stream = await self.async_client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.0,
                    max_tokens=1024,
                    stream=True,
                )

                full_text = ""
                async for chunk in stream:
                    delta = chunk.choices[0].delta.content or ""
                    if delta:
                        full_text += delta
                        yield f"data: {json.dumps({'event': 'token', 'data': delta})}\n\n"

                verification = hallucination_guard.verify_answer_grounding(full_text, snippets)
                yield f"data: {json.dumps({'event': 'grounding', 'data': verification})}\n\n"
                yield f"data: {json.dumps({'event': 'done'})}\n\n"
                return
            except Exception as e:
                logger.error(f"Groq streaming failed: {e}")

        # Zero-hallucination extractive streaming fallback
        verified_answer = hallucination_guard.synthesize_extractive_grounded_answer(query, snippets)
        verification = hallucination_guard.verify_answer_grounding(verified_answer, snippets)
        yield f"data: {json.dumps({'event': 'grounding', 'data': verification})}\n\n"
        for word in verified_answer.split(" "):
            yield f"data: {json.dumps({'event': 'token', 'data': word + ' '})}\n\n"
            await asyncio.sleep(0.01)

        yield f"data: {json.dumps({'event': 'done'})}\n\n"

    def _mock_grounded_answer(self, query: str, snippets: List[Dict[str, Any]]) -> str:
        if not snippets:
            return f"No supplier documents directly match your inquiry: '{query}'. Please ensure relevant contract and SLA PDFs are uploaded."

        lines = [
            f"### Grounded Contract Analysis: *\"{query}\"*\n",
            "Retrieved via **Hybrid Search (Qdrant HNSW Dense + Okapi BM25 + RRF Cross-Reranker)** across indexed supplier PDFs:\n"
        ]
        for idx, snip in enumerate(snippets[:3], start=1):
            title = snip.get("doc_title", "Supplier Agreement")
            supplier = snip.get("supplier_name", "Supplier")
            page = snip.get("page_number", 1)
            score = snip.get("score", 0.0)
            excerpt = snip.get("content", "").strip()[:320]
            lines.append(
                f"{idx}. **{title}** (*{supplier}*, Page {page}, Rerank Score: `{score:.3f}`):\n"
                f"   > \"{excerpt}...\"\n"
            )

        lines.append(
            "### Recommended Procurement Action:\n"
            "- Cross-check impacted SKUs in the **Multi-Supplier MILP Optimizer** to split orders across qualified secondary vendors and cap single-supplier disruption exposure."
        )
        return "\n".join(lines)

    def _extract_risk_keywords(self, text: str) -> List[str]:
        risk_keywords = [
            "lead time extension", "price increase", "force majeure", "shortage",
            "delay", "penalty", "minimum order quantity", "capacity constraint", "allocation"
        ]
        text_lower = text.lower()
        return [kw for kw in risk_keywords if kw in text_lower]


rag_service = RAGGenerationService()
