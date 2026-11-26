from functools import lru_cache
from typing import List, Union, Tuple
import numpy as np
from app.config import settings
from app.core.logging import logger

try:
    from fastembed import TextEmbedding
    FASTEMBED_AVAILABLE = True
except ImportError:
    FASTEMBED_AVAILABLE = False
    logger.warning("fastembed not installed. Falling back to local deterministic embedding generator.")


class EmbeddingService:
    """
    Generates high quality dense vector embeddings using BAAI/bge-small-en-v1.5 with:
    - In-memory LRU query caching for sub-millisecond query embedding
    - Batched parallel document vector generation
    """
    _instance = None
    _model = None
    _model_initialized = False
    DIMENSION = 384
    BATCH_SIZE = 64

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
        return cls._instance

    def _ensure_model(self):
        if not self._model_initialized:
            self._model_initialized = True
            if FASTEMBED_AVAILABLE:
                try:
                    logger.info("Initializing FastEmbed BGE-small-en-v1.5 model...")
                    self._model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
                    logger.info("FastEmbed BGE-small-en-v1.5 model initialized successfully.")
                except Exception as e:
                    logger.warning(f"Could not load FastEmbed model: {e}. Utilizing fallback embedder.")
                    self._model = None

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        self._ensure_model()
        if self._model is not None:
            try:
                all_embeddings: List[List[float]] = []
                # Chunk texts into optimal batch sizes
                for i in range(0, len(texts), self.BATCH_SIZE):
                    batch = texts[i:i + self.BATCH_SIZE]
                    batch_embeddings = list(self._model.embed(batch))
                    all_embeddings.extend([emb.tolist() for emb in batch_embeddings])
                return all_embeddings
            except Exception as e:
                logger.error(f"Error during document embedding: {e}")

        # High-entropy deterministic fallback embedding for offline/testing environments
        return [self._fallback_embed(text) for text in texts]

    def embed_query(self, text: str) -> List[float]:
        return list(self._cached_embed_query(text.strip()))

    @lru_cache(maxsize=2048)
    def _cached_embed_query(self, text: str) -> Tuple[float, ...]:
        """
        LRU-cached single query vector generation for ultra-fast RAG retrieval.
        """
        vector = self.embed_documents([text])[0]
        return tuple(vector)

    def _fallback_embed(self, text: str) -> List[float]:
        """
        Deterministic normalized vector representation for offline test resilience.
        """
        import hashlib
        np.random.seed(int(hashlib.md5(text.encode("utf-8")).hexdigest()[:8], 16) % 2**32)
        vec = np.random.randn(self.DIMENSION).astype(float)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()


embedding_service = EmbeddingService()
