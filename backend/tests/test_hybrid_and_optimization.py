import os
import tempfile
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.rag.ingestion import DocumentIngestionService
from app.services.rag.retrieval import QdrantVectorStore
from app.services.optimization.supplier_optimizer import MultiSupplierMILPOptimizer, SupplierOption
from scripts.generate_sample_pdfs import generate_all_sample_pdfs


@pytest.fixture(scope="module")
def multi_pdf_hybrid_store():
    """
    Generates all 6 multi-page enterprise supplier PDFs into a temporary directory,
    extracts pages via PyMuPDF, and indexes them into an isolated Hybrid Qdrant + BM25 store.
    """
    store = QdrantVectorStore()
    store.client = None  # Force isolated in-memory + BM25 hybrid store so prod storage is untouched
    store._in_memory_docs.clear()
    store._bm25.clear()
    store._bm25_collection_name = store.collection_name

    ingestor = DocumentIngestionService(chunk_size=600, chunk_overlap=100)

    with tempfile.TemporaryDirectory() as tmpdir:
        pdfs = generate_all_sample_pdfs(tmpdir)
        assert len(pdfs) == 6

        for idx, meta in enumerate(pdfs):
            assert os.path.exists(meta["file_path"])
            pages = ingestor.extract_text_from_pdf(meta["file_path"])
            assert len(pages) == meta["pages"], f"Expected {meta['pages']} pages in {meta['filename']}"

            chunks = []
            c_idx = 0
            for p in pages:
                for ch in ingestor.chunk_text(p["text"], p["page_number"]):
                    chunks.append({
                        "doc_id": f"pdf-doc-{idx}",
                        "doc_title": meta["title"],
                        "supplier_id": meta["supplier_code"],
                        "supplier_name": meta["title"].split(" ")[0] + " " + meta["title"].split(" ")[1],
                        "doc_type": meta["doc_type"],
                        "page_number": ch["page_number"],
                        "chunk_index": c_idx,
                        "content": ch["content"],
                    })
                    c_idx += 1
            store.upsert_chunks(chunks)

    return store


def test_multi_pdf_hybrid_rrf_retrieval_accuracy(multi_pdf_hybrid_store):
    """
    Verifies Hybrid RRF + Cross-Reranker accurately retrieves exact legal clauses,
    addendums, SKU codes, and percentages across all 6 multi-page PDFs.
    """
    test_cases = [
        ("Section 7.2 liquidated damages 2.0% weekly cap 12% Apex", "SUP-APEX", "2.0%"),
        ("ADD-APEX-2026-Q2 6% volume pricing discount 1,500 units SKU-MCU-32B", "SUP-APEX", "6%"),
        ("What is the 12.5% logistics energy surcharge effective March 1 2026?", "SUP-PACIFIC", "12.5%"),
        ("Malacca Strait maritime congestion 35-42 calendar days SKU-LENS-4K", "SUP-PACIFIC", "35-42"),
        ("FOB Oslo 14-day lead time 1.5% weekly penalty Nordic", "SUP-NORDIC", "1.5%"),
        ("EuroOptics Cleanroom ISO Class 5 0.02% defect tolerance $21.40", "SUP-EUROOPTICS", "ISO Class 5"),
        ("Titan IP67 waterproof ISO 9001:2015 overnight dispatch", "SUP-TITAN", "IP67"),
    ]

    for query, expected_supplier, expected_token in test_cases:
        results = multi_pdf_hybrid_store.search(query, top_k=3, mode="hybrid")
        assert len(results) >= 1
        top = results[0]
        assert top["supplier_id"] == expected_supplier, f"Query '{query}' returned {top['supplier_id']}"
        assert expected_token.lower() in top["content"].lower()
        assert top["retrieval_method"] == "hybrid_rrf_reranked"
        assert top["bm25_score"] > 0
        assert top["rrf_score"] > 0


def test_retrieval_modes_and_metadata_isolation(multi_pdf_hybrid_store):
    """
    Verifies dense, bm25, and hybrid modes all function properly and respect doc_type filters.
    """
    for mode in ("dense", "bm25", "hybrid"):
        res = multi_pdf_hybrid_store.search(
            "SKU-MCU-32B tiered volume pricing addendum",
            top_k=3,
            doc_type="addendum",
            mode=mode,
        )
        assert len(res) >= 1
        for item in res:
            assert item["doc_type"] == "addendum"
            assert item["supplier_id"] == "SUP-APEX"


def test_milp_optimizer_splits_high_risk_orders_optimally():
    """
    Tests SciPy HiGHS MILP solver on SKU-LENS-4K competing Pacific Optics (high disruption + 12.5% surcharge)
    against EuroOptics GmbH (higher base cost, 0% surcharge, 97% reliability).
    """
    suppliers = [
        SupplierOption(
            supplier_id="sup-pacific",
            supplier_name="Pacific Precision Optics",
            supplier_code="SUP-PACIFIC",
            country="Singapore",
            unit_cost=18.50,
            surcharge_pct=12.5,
            lead_time_days=35,
            reliability_score=0.78,
            disruption_risk_score=65.0,
            moq=100,
            max_capacity=1500,
            fixed_order_cost=220.0,
        ),
        SupplierOption(
            supplier_id="sup-euro",
            supplier_name="EuroOptics Precision GmbH",
            supplier_code="SUP-EUROOPTICS",
            country="Germany",
            unit_cost=21.40,
            surcharge_pct=0.0,
            lead_time_days=18,
            reliability_score=0.97,
            disruption_risk_score=10.0,
            moq=100,
            max_capacity=1200,
            fixed_order_cost=180.0,
        ),
        SupplierOption(
            supplier_id="sup-apex",
            supplier_name="Apex Microelectronics",
            supplier_code="SUP-APEX",
            country="Taiwan",
            unit_cost=22.80,
            surcharge_pct=0.0,
            lead_time_days=21,
            reliability_score=0.94,
            disruption_risk_score=15.0,
            moq=100,
            max_capacity=1000,
            fixed_order_cost=200.0,
        ),
    ]

    result = MultiSupplierMILPOptimizer.solve(
        sku="SKU-LENS-4K",
        total_demand_qty=600,
        suppliers=suppliers,
        risk_aversion_lambda=1.5,
        max_single_supplier_share=0.70,
        target_lead_time_days=18,
    )

    assert result["solver_status"] == "OPTIMAL"
    assert result["total_allocated_quantity"] >= 600
    assert len(result["allocations"]) >= 2

    # Concentration cap respected (<= 70% to any single supplier)
    for alloc in result["allocations"]:
        assert alloc["allocation_share_pct"] <= 70.1
        assert alloc["allocated_units"] >= alloc["moq"]

    # Risk-averse MILP must beat naive single-source Pacific Optics on risk-adjusted cost and disruption risk
    assert result["summary"]["expected_risk_cost_savings"] > 0
    assert result["summary"]["disruption_risk_reduction_pct"] > 50.0
    # EuroOptics should receive the primary allocation over disrupted Pacific Optics
    assert result["allocations"][0]["supplier_code"] == "SUP-EUROOPTICS"


def test_milp_optimizer_edge_cases():
    with pytest.raises(ValueError):
        MultiSupplierMILPOptimizer.solve("SKU-TEST", 0, [])

    single_sup = [
        SupplierOption("s1", "Solo Supplier", "SUP-1", "US", unit_cost=10.0, moq=200, max_capacity=1000)
    ]
    # Small demand with strict cap on single supplier should gracefully relax and still return OPTIMAL
    res = MultiSupplierMILPOptimizer.solve(
        sku="SKU-SOLO",
        total_demand_qty=50,
        suppliers=single_sup,
        max_single_supplier_share=0.5,
    )
    assert res["solver_status"] == "OPTIMAL"
    assert res["total_allocated_quantity"] >= 50
    assert len(res["solver_notes"]) >= 1


def test_api_optimization_benchmark_and_security_headers():
    """
    Hermetic end-to-end API integration test for:
      - POST /api/v1/optimization/allocate
      - GET /api/v1/optimization/evaluate
      - POST /api/v1/chat (hybrid mode)
      - Production Security Headers on /health
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool
    from app.db.base import Base
    from app.dependencies import get_db
    from app.db.models.supplier import Supplier
    from app.db.models.product import Product
    from app.db.models.inventory import Inventory

    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    seed_db = TestSession()
    sup_pac = Supplier(
        code="SUP-PACIFIC", name="Pacific Precision Optics", country="Singapore",
        base_lead_time_days=35, reliability_score=0.78, quality_score=0.91, disruption_risk_score=65.0
    )
    sup_euro = Supplier(
        code="SUP-EUROOPTICS", name="EuroOptics Precision GmbH", country="Germany",
        base_lead_time_days=18, reliability_score=0.97, quality_score=0.996, disruption_risk_score=10.0
    )
    seed_db.add_all([sup_pac, sup_euro])
    seed_db.flush()

    prod = Product(
        sku="SKU-LENS-4K", name="Optical 4K Sensor Glass Lens Array",
        category="Optoelectronics", unit_cost=18.50, unit_price=42.00,
        lead_time_days=35, supplier_id=sup_pac.id
    )
    seed_db.add(prod)
    seed_db.flush()
    seed_db.add(Inventory(product_id=prod.id, current_stock=45, reorder_point=120, reorder_quantity=250))
    seed_db.commit()
    seed_db.close()

    def _override_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    prev_override = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = _override_db

    try:
        with TestClient(app) as client:
            # 1. Health & Security Headers
            h = client.get("/health")
            assert h.status_code == 200
            assert h.headers.get("X-Content-Type-Options") == "nosniff"
            assert h.headers.get("X-Frame-Options") == "DENY"
            assert h.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"

            # 2. Multi-Supplier MILP Allocate Endpoint
            opt_res = client.post(
                "/api/v1/optimization/allocate",
                json={
                    "sku": "SKU-LENS-4K",
                    "required_quantity": 600,
                    "risk_aversion_lambda": 1.5,
                    "max_single_supplier_share": 0.70,
                },
            )
            assert opt_res.status_code == 200
            opt_body = opt_res.json()
            assert opt_body["solver_status"] == "OPTIMAL"
            assert opt_body["summary"]["expected_risk_cost_savings"] > 0

            # 3. Empirical RAG Ablation Evaluation Endpoint
            eval_res = client.get("/api/v1/optimization/evaluate?include_forecasting=false&force_refresh=true")
            assert eval_res.status_code == 200
            eval_body = eval_res.json()
            rag_eval = eval_body["rag_evaluation"]
            assert rag_eval["modes"]["hybrid"]["hit_at_1_pct"] >= 80.0
            assert rag_eval["modes"]["hybrid"]["mrr"] >= 0.85

            # 4. Hybrid RAG Chat Endpoint
            chat_res = client.post(
                "/api/v1/chat",
                json={
                    "query": "What is EuroOptics cleanroom ISO class and defect tolerance for SKU-LENS-4K?",
                    "retrieval_mode": "hybrid",
                    "stream": False,
                },
            )
            assert chat_res.status_code == 200
            chat_body = chat_res.json()
            assert chat_body["retrieval_mode"] == "hybrid"
            assert len(chat_body["citations"]) >= 1
            assert chat_body["citations"][0]["retrieval_method"] == "hybrid_rrf_reranked"
    finally:
        if prev_override is not None:
            app.dependency_overrides[get_db] = prev_override
        else:
            app.dependency_overrides.pop(get_db, None)
        Base.metadata.drop_all(bind=test_engine)
