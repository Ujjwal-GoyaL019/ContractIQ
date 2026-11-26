import pytest
from app.services.rag.ingestion import DocumentIngestionService
from app.services.rag.embedding import embedding_service
from app.services.rag.retrieval import vector_store
from app.services.rag.generation import rag_service


def test_embedding_service():
    texts = ["Supplier delivery SLA terms", "Microcontroller demand spike"]
    embeddings = embedding_service.embed_documents(texts)
    assert len(embeddings) == 2
    assert len(embeddings[0]) == embedding_service.DIMENSION


def test_chunking_service():
    service = DocumentIngestionService(chunk_size=100, chunk_overlap=20)
    sample_text = (
        "This is a sample supplier contract clause. "
        "Standard lead time is fourteen calendar days. "
        "Force majeure clauses apply during regional port congestion and raw material allocations."
    )
    chunks = service.chunk_text(sample_text, page_number=1)
    assert len(chunks) >= 1
    for c in chunks:
        assert "content" in c
        assert "page_number" in c
        assert c["page_number"] == 1


def test_vector_store_and_search():
    test_chunks = [
        {
            "doc_id": "test-doc-001",
            "doc_title": "Apex Supply Terms",
            "supplier_id": "sup-apex",
            "supplier_name": "Apex Micro",
            "page_number": 1,
            "chunk_index": 0,
            "doc_type": "contract",
            "content": "Apex guarantees 21 days lead time with a 20% surcharge for expedited deliveries."
        }
    ]
    upserted = vector_store.upsert_chunks(test_chunks)
    assert upserted >= 1

    results = vector_store.search("expedited lead time surcharge", top_k=1)
    assert len(results) >= 1
    assert "score" in results[0]
    assert "Apex" in results[0]["content"] or "Apex" in results[0]["doc_title"]


def test_rag_generation_mock():
    res = rag_service.answer_query("What are the expedited terms for Apex?", supplier_id="sup-apex")
    assert "answer" in res
    assert len(res["answer"]) > 20
    assert "citations" in res
