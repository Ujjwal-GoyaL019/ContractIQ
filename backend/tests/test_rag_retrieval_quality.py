import pytest
from app.services.rag.retrieval import QdrantVectorStore
from app.services.rag.embedding import EmbeddingService


@pytest.fixture(scope="module")
def populated_vector_store():
    store = QdrantVectorStore()
    store.collection_name = "test_retrieval_quality"
    store.dimension = 384
    store._in_memory_docs.clear()

    # Ingest 3 rich semantic documents
    chunks = [
        # Document 1: Apex Microelectronics
        {
            "doc_id": "doc-apex-01",
            "doc_title": "Apex Master Supply Agreement 2026",
            "supplier_id": "sup-apex",
            "supplier_name": "Apex Microelectronics",
            "page_number": 3,
            "chunk_index": 0,
            "doc_type": "contract",
            "content": "Expedited orders requested with less than fourteen (14) days notice incur a mandatory 15% rush surcharge fee. Active force majeure clause applies in case of semiconductor wafer packaging disruptions."
        },
        # Document 2: Nordic Silicon
        {
            "doc_id": "doc-nordic-01",
            "doc_title": "Nordic Silicon Procurement Terms",
            "supplier_id": "sup-nordic",
            "supplier_name": "Nordic Silicon",
            "page_number": 1,
            "chunk_index": 0,
            "doc_type": "sla",
            "content": "Nordic Silicon guarantees standard delivery within 14 calendar days. Minimum Order Quantity (MOQ) is strictly 5,000 units. Standard hardware replacement warranty period is twenty-four (24) months."
        },
        # Document 3: Pacific Precision Optics
        {
            "doc_id": "doc-pacific-01",
            "doc_title": "Pacific Precision Optics Quality Compliance",
            "supplier_id": "sup-pacific",
            "supplier_name": "Pacific Precision Optics",
            "page_number": 2,
            "chunk_index": 0,
            "doc_type": "compliance",
            "content": "Optical lens manufacturing complies with Cleanroom ISO Class 5 standards. Maximum allowable defect tolerance is set at 0.02% across all optical batch lots."
        }
    ]

    store.upsert_chunks(chunks)
    return store


def test_rag_semantic_relevance_top1(populated_vector_store):
    """
    Test that specific contractual queries accurately retrieve the corresponding document in rank 1.
    """
    # 1. Query targeting Apex expedited fee
    apex_results = populated_vector_store.search("What is the surcharge fee for expedited rush delivery?", top_k=1)
    assert len(apex_results) >= 1
    assert apex_results[0]["supplier_id"] == "sup-apex"
    assert "15% rush surcharge fee" in apex_results[0]["content"]

    # 2. Query targeting Nordic MOQ and warranty
    nordic_results = populated_vector_store.search("What is the minimum order quantity and warranty duration?", top_k=1)
    assert len(nordic_results) >= 1
    assert nordic_results[0]["supplier_id"] == "sup-nordic"
    assert "5,000 units" in nordic_results[0]["content"]

    # 3. Query targeting Pacific Cleanroom standard
    pacific_results = populated_vector_store.search("Which cleanroom ISO class standard and defect rate are required?", top_k=1)
    assert len(pacific_results) >= 1
    assert pacific_results[0]["supplier_id"] == "sup-pacific"
    assert "ISO Class 5" in pacific_results[0]["content"]


def test_rag_supplier_metadata_filtering(populated_vector_store):
    """
    Test that supplier_id metadata filter strictly restricts retrieved chunks to the specified supplier.
    """
    # Ask generic query with strict supplier_id filter
    results = populated_vector_store.search("delivery terms and conditions", top_k=5, supplier_id="sup-nordic")
    assert len(results) >= 1
    for r in results:
        assert r["supplier_id"] == "sup-nordic"


def test_rag_doc_type_metadata_filtering(populated_vector_store):
    """
    Test that doc_type metadata filter strictly filters by document category.
    """
    results = populated_vector_store.search("standards and tolerances", top_k=5, doc_type="compliance")
    assert len(results) >= 1
    for r in results:
        assert r["doc_type"] == "compliance"
        assert r["supplier_id"] == "sup-pacific"
