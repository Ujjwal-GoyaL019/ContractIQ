from typing import List, Dict, Any, Optional
import os
import uuid
import numpy as np
from app.config import settings
from app.core.logging import logger
from app.services.rag.embedding import embedding_service
from app.services.rag.hybrid_retriever import BM25SparseIndex, HybridRRFReranker

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models as qmodels
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    logger.warning("qdrant-client not installed. In-memory vector index fallback active.")


class QdrantVectorStore:
    """
    Hybrid Vector + Lexical Retrieval Engine powered by Qdrant (HNSW Dense) + Okapi BM25 (Sparse)
    with Reciprocal Rank Fusion (RRF) and Second-Stage Calibrated Cross-Reranking.
    """

    def __init__(self):
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        self.dimension = embedding_service.DIMENSION
        self.client = None
        self._in_memory_docs: List[Dict[str, Any]] = []
        self._bm25 = BM25SparseIndex(k1=1.5, b=0.75)
        self._reranker = HybridRRFReranker(rrf_k=60, dense_weight=0.6, bm25_weight=0.4)
        self._bm25_collection_name: Optional[str] = None
        self._init_client()

    def _init_client(self):
        if not QDRANT_AVAILABLE:
            return

        try:
            if settings.QDRANT_URL.startswith("http://") or settings.QDRANT_URL.startswith("https://"):
                self.client = QdrantClient(
                    url=settings.QDRANT_URL,
                    api_key=settings.QDRANT_API_KEY if settings.QDRANT_API_KEY else None,
                    timeout=10.0
                )
            elif settings.QDRANT_URL == ":memory:":
                self.client = QdrantClient(":memory:")
            else:
                os.makedirs(settings.QDRANT_URL, exist_ok=True)
                self.client = QdrantClient(path=settings.QDRANT_URL)

            self._ensure_collection()
            self._sync_bm25_from_qdrant()
            logger.info(
                f"Qdrant hybrid store initialized on {settings.QDRANT_URL} "
                f"(BM25 hydrated with {self._bm25.size} chunks)."
            )
        except Exception as e:
            logger.warning(f"Could not connect to Qdrant ({e}). Falling back to local in-memory hybrid index.")
            self.client = None

    def _ensure_collection(self):
        if self.client is None:
            return
        try:
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)
            if not exists:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=qmodels.VectorParams(
                        size=self.dimension,
                        distance=qmodels.Distance.COSINE
                    ),
                    hnsw_config=qmodels.HnswConfigDiff(
                        m=16,
                        ef_construct=100,
                        full_scan_threshold=10000
                    )
                )
                logger.info(f"Created Qdrant collection with HNSW index: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error ensuring Qdrant collection: {e}")

    def _sync_bm25_from_qdrant(self):
        """
        Hydrates the in-memory Okapi BM25 index from all stored payloads in the active Qdrant collection.
        """
        self._bm25.clear()
        self._bm25_collection_name = self.collection_name
        if self.client is None:
            if self._in_memory_docs:
                self._bm25.add_documents([d["payload"] for d in self._in_memory_docs])
            return

        try:
            self._ensure_collection()
            all_payloads: List[Dict[str, Any]] = []
            offset = None
            while True:
                points, next_offset = self.client.scroll(
                    collection_name=self.collection_name,
                    limit=256,
                    offset=offset,
                    with_payload=True,
                    with_vectors=False
                )
                for pt in points:
                    if pt.payload:
                        all_payloads.append(dict(pt.payload))
                if next_offset is None or not points:
                    break
                offset = next_offset

            if all_payloads:
                self._bm25.add_documents(all_payloads)
        except Exception as e:
            logger.warning(f"Could not hydrate BM25 from Qdrant ({e}).")

    def reset_collection(self):
        """
        Clears all points from the active collection and resets the BM25 index (used during re-seeding).
        """
        self._in_memory_docs.clear()
        self._bm25.clear()
        self._bm25_collection_name = self.collection_name
        if self.client is not None:
            try:
                collections = self.client.get_collections().collections
                if any(c.name == self.collection_name for c in collections):
                    self.client.delete_collection(collection_name=self.collection_name)
                self._ensure_collection()
                logger.info(f"Reset Qdrant collection: {self.collection_name}")
            except Exception as e:
                logger.warning(f"Failed to reset Qdrant collection: {e}")

    def upsert_chunks(self, chunks: List[Dict[str, Any]]) -> int:
        """
        Upsert a batch of text chunks with metadata and embeddings into both Qdrant (Dense)
        and Okapi BM25 (Sparse) indexes.
        """
        if not chunks:
            return 0

        if self._bm25_collection_name != self.collection_name:
            self._sync_bm25_from_qdrant()

        texts = [c["content"] for c in chunks]
        embeddings = embedding_service.embed_documents(texts)

        payloads = [
            {
                "doc_id": chunk["doc_id"],
                "doc_title": chunk.get("doc_title", ""),
                "supplier_id": chunk.get("supplier_id"),
                "supplier_name": chunk.get("supplier_name", ""),
                "page_number": chunk.get("page_number", 1),
                "chunk_index": chunk.get("chunk_index", i),
                "doc_type": chunk.get("doc_type", "contract"),
                "content": chunk["content"],
            }
            for i, chunk in enumerate(chunks)
        ]

        # Always keep BM25 sparse index updated
        self._bm25.add_documents(payloads)

        if self.client is not None:
            try:
                self._ensure_collection()
                points = []
                for payload, emb in zip(payloads, embeddings):
                    point_id = str(
                        uuid.uuid5(
                            uuid.NAMESPACE_DNS,
                            f"{payload['doc_id']}_{payload['chunk_index']}"
                        )
                    )
                    points.append(
                        qmodels.PointStruct(
                            id=point_id,
                            vector=emb,
                            payload=payload
                        )
                    )
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=points,
                    wait=True
                )
                return len(points)
            except Exception as e:
                logger.error(f"Failed to upsert to Qdrant: {e}. Storing in memory fallback.")

        # In-memory store fallback
        for payload, emb in zip(payloads, embeddings):
            self._in_memory_docs.append({
                "payload": payload,
                "vector": emb
            })
        return len(chunks)

    def _dense_search(
        self,
        query: str,
        top_k: int = 20,
        supplier_id: Optional[str] = None,
        doc_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        query_vector = embedding_service.embed_query(query)

        if self.client is not None:
            try:
                must_conditions = []
                if supplier_id:
                    must_conditions.append(
                        qmodels.FieldCondition(
                            key="supplier_id",
                            match=qmodels.MatchValue(value=supplier_id)
                        )
                    )
                if doc_type:
                    must_conditions.append(
                        qmodels.FieldCondition(
                            key="doc_type",
                            match=qmodels.MatchValue(value=doc_type)
                        )
                    )

                query_filter = qmodels.Filter(must=must_conditions) if must_conditions else None

                if hasattr(self.client, "query_points"):
                    res = self.client.query_points(
                        collection_name=self.collection_name,
                        query=query_vector,
                        query_filter=query_filter,
                        limit=top_k
                    )
                    search_result = res.points
                elif hasattr(self.client, "search"):
                    search_result = self.client.search(
                        collection_name=self.collection_name,
                        query_vector=query_vector,
                        query_filter=query_filter,
                        limit=top_k
                    )
                else:
                    search_result = []

                results = []
                for scored_point in search_result:
                    payload = scored_point.payload or {}
                    results.append({
                        "doc_id": payload.get("doc_id", ""),
                        "doc_title": payload.get("doc_title", "Document"),
                        "supplier_id": payload.get("supplier_id"),
                        "supplier_name": payload.get("supplier_name", "Unknown Supplier"),
                        "page_number": payload.get("page_number", 1),
                        "content": payload.get("content", ""),
                        "score": round(float(scored_point.score), 4),
                        "dense_score": round(float(scored_point.score), 4),
                        "bm25_score": 0.0,
                        "rrf_score": 0.0,
                        "retrieval_method": "dense_hnsw",
                        "doc_type": payload.get("doc_type", "contract")
                    })
                return results
            except Exception as e:
                logger.error(f"Error during Qdrant search: {e}")

        # In-memory dense cosine fallback
        results = []
        q_vec = np.array(query_vector)
        for doc in self._in_memory_docs:
            payload = doc["payload"]
            if supplier_id and payload.get("supplier_id") != supplier_id:
                continue
            if doc_type and payload.get("doc_type") != doc_type:
                continue

            d_vec = np.array(doc["vector"])
            denom = np.linalg.norm(q_vec) * np.linalg.norm(d_vec)
            sim = float(np.dot(q_vec, d_vec) / denom) if denom > 0 else 0.0

            results.append({
                "doc_id": payload.get("doc_id", ""),
                "doc_title": payload.get("doc_title", "Document"),
                "supplier_id": payload.get("supplier_id"),
                "supplier_name": payload.get("supplier_name", "Unknown Supplier"),
                "page_number": payload.get("page_number", 1),
                "content": payload.get("content", ""),
                "score": round(sim, 4),
                "dense_score": round(sim, 4),
                "bm25_score": 0.0,
                "rrf_score": 0.0,
                "retrieval_method": "dense_cosine",
                "doc_type": payload.get("doc_type", "contract")
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def search(
        self,
        query: str,
        top_k: int = 5,
        supplier_id: Optional[str] = None,
        doc_type: Optional[str] = None,
        mode: str = "hybrid"
    ) -> List[Dict[str, Any]]:
        """
        Executes retrieval across indexed supplier documents.
        Modes:
          - 'hybrid' (default): Dense HNSW + Okapi BM25 -> Reciprocal Rank Fusion -> Cross-Reranker
          - 'dense': Pure semantic vector cosine search
          - 'bm25': Pure lexical Okapi BM25 search
        """
        if self._bm25_collection_name != self.collection_name:
            self._sync_bm25_from_qdrant()
        elif self.client is None and self._bm25.size != len(self._in_memory_docs):
            self._bm25.clear()
            self._bm25.add_documents([d["payload"] for d in self._in_memory_docs])

        if mode == "dense":
            return self._dense_search(query, top_k=top_k, supplier_id=supplier_id, doc_type=doc_type)

        if mode == "bm25":
            bm25_hits = self._bm25.search(query, top_k=top_k, supplier_id=supplier_id, doc_type=doc_type)
            for item in bm25_hits:
                item["dense_score"] = 0.0
                item["rrf_score"] = 0.0
                item["retrieval_method"] = "bm25_sparse"
            return bm25_hits

        # Default: Hybrid Search (Fetch candidate pool -> RRF Fusion -> Cross-Rerank)
        candidate_k = max(top_k * 4, 20)
        dense_candidates = self._dense_search(
            query, top_k=candidate_k, supplier_id=supplier_id, doc_type=doc_type
        )
        bm25_candidates = self._bm25.search(
            query, top_k=candidate_k, supplier_id=supplier_id, doc_type=doc_type
        )

        return self._reranker.fuse_and_rerank(
            query=query,
            dense_results=dense_candidates,
            bm25_results=bm25_candidates,
            top_k=top_k
        )


vector_store = QdrantVectorStore()
