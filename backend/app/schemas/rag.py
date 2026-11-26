from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, model_validator


class DocumentMetadata(BaseModel):
    id: str
    title: str
    filename: str
    doc_type: str
    supplier_id: Optional[str] = None
    supplier_name: Optional[str] = None
    chunk_count: int
    file_size_bytes: int
    created_at: datetime
    summary: Optional[str] = None

    class Config:
        from_attributes = True


class Citation(BaseModel):
    doc_id: str
    document_title: str
    supplier_name: Optional[str] = None
    page_number: Optional[int] = 1
    snippet: str
    score: float
    dense_score: Optional[float] = None
    bm25_score: Optional[float] = None
    rrf_score: Optional[float] = None
    retrieval_method: Optional[str] = "hybrid_rrf_reranked"


class ChatMessage(BaseModel):
    role: str = Field(..., example="user") # user, assistant, system
    content: str = Field(...)


class ChatRequest(BaseModel):
    query: Optional[str] = Field(None, example="Which suppliers have force majeure or lead-time risk clauses for MCU chips?")
    question: Optional[str] = None
    supplier_id: Optional[str] = None
    sku: Optional[str] = None
    retrieval_mode: str = Field("hybrid", description="Retrieval engine mode: 'hybrid', 'dense', or 'bm25'")
    conversation_history: Optional[List[ChatMessage]] = []
    stream: bool = Field(False, description="Whether to stream response via SSE")

    @model_validator(mode="before")
    @classmethod
    def reconcile_query(cls, values):
        if isinstance(values, dict):
            if not values.get("query") and values.get("question"):
                values["query"] = values["question"]
            elif not values.get("query"):
                values["query"] = "General supply chain inquiry"
        return values



class GroundingVerification(BaseModel):
    is_grounded: bool = True
    abstained: bool = False
    faithfulness_score: float = 1.0
    verified_claims_count: int = 0
    unsupported_claims: List[str] = []
    abstention_reason: Optional[str] = None
    verification_method: str = "deterministic_claim_entity_audit"


class ChatResponse(BaseModel):
    answer: str
    citations: List[Citation] = []
    grounded_skus: List[str] = []
    risk_flags_detected: List[str] = []
    suggested_followups: List[str] = []
    retrieval_mode: str = "hybrid"
    grounding_verification: Optional[GroundingVerification] = None
