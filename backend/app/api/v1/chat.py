from typing import List
from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas.rag import ChatRequest, ChatResponse, Citation, GroundingVerification
from app.services.rag.generation import rag_service

router = APIRouter(prefix="/chat", tags=["RAG Intelligence Chat"])


@router.post("", response_model=ChatResponse)
async def chat_with_supplier_docs(req: ChatRequest, db: Session = Depends(get_db)):
    """
    RAG conversational query endpoint over supplier documents and operational risks.
    Supports regular JSON response or Server-Sent Events (SSE) streaming.
    """
    history_dicts = [m.model_dump() for m in req.conversation_history] if req.conversation_history else None

    mode = req.retrieval_mode if req.retrieval_mode in ("hybrid", "dense", "bm25") else "hybrid"

    if req.stream:
        return StreamingResponse(
            rag_service.stream_query(
                query=req.query,
                supplier_id=req.supplier_id,
                top_k=5,
                conversation_history=history_dicts,
                retrieval_mode=mode
            ),
            media_type="text/event-stream"
        )

    result = rag_service.answer_query(
        query=req.query,
        supplier_id=req.supplier_id,
        top_k=5,
        conversation_history=history_dicts,
        retrieval_mode=mode
    )

    citations = [Citation(**c) for c in result.get("citations", [])]
    gv_raw = result.get("grounding_verification")
    gv = GroundingVerification(**gv_raw) if gv_raw else None

    return ChatResponse(
        answer=result["answer"],
        citations=citations,
        grounded_skus=[req.sku] if req.sku else [],
        risk_flags_detected=result.get("risk_flags_detected", []),
        suggested_followups=result.get("suggested_followups", []),
        retrieval_mode=mode,
        grounding_verification=gv,
    )
