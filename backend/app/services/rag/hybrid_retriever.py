from typing import List, Dict, Any, Optional, Tuple
import math
import re
from collections import Counter


# Preserve SKUs (SKU-MCU-32B), clause numbers (7.2, 4.2b), percentages (12.5%), ISO codes
TOKEN_PATTERN = re.compile(r"[a-z0-9]+(?:[-./%][a-z0-9]+)*%?", re.IGNORECASE)

STOPWORDS = {
    "the", "a", "an", "and", "or", "for", "of", "to", "in", "on", "at", "by",
    "with", "is", "are", "was", "were", "be", "been", "being", "that", "this",
    "it", "as", "from", "will", "shall", "can", "may", "our", "we", "you",
    "what", "which", "who", "how", "when", "where", "does", "do", "did", "have",
    "has", "had", "not", "no", "all", "any", "if", "per", "such", "under",
}


def tokenize_legal(text: str) -> List[str]:
    """
    Domain-aware tokenizer for supply chain contracts.
    Retains compound identifiers like 'sku-lens-4k', '12.5%', 'iso', '7.2', 'moq'.
    """
    if not text:
        return []
    raw_tokens = TOKEN_PATTERN.findall(text.lower())
    tokens: List[str] = []
    for tok in raw_tokens:
        cleaned = tok.strip(".-/")
        if not cleaned or cleaned in STOPWORDS:
            continue
        tokens.append(cleaned)
        # Also emit sub-parts for hyphenated SKUs or compound terms so partial matches work
        if "-" in cleaned:
            for part in cleaned.split("-"):
                if part and part not in STOPWORDS and len(part) >= 2:
                    tokens.append(part)
    return tokens


def extract_high_value_entities(text: str) -> List[str]:
    """
    Extracts exact legal/supply-chain entities (SKUs, percentages, ISO specs, clause numbers, currency).
    """
    if not text:
        return []
    entities = set()
    for match in re.findall(r"\bsku-[a-z0-9-]+\b", text, re.IGNORECASE):
        entities.add(match.lower())
    for match in re.findall(r"\b\d+(?:\.\d+)?%\b", text):
        entities.add(match.lower())
    for match in re.findall(r"\biso\s*(?:class\s*)?\d+(?::\d+)?\b", text, re.IGNORECASE):
        entities.add(re.sub(r"\s+", " ", match.lower()))
    for match in re.findall(r"\b(?:section|clause|article)\s+\d+(?:\.\d+)*\b", text, re.IGNORECASE):
        entities.add(re.sub(r"\s+", " ", match.lower()))
    for match in re.findall(r"\b\d{1,3}(?:,\d{3})+\b", text):
        entities.add(match.replace(",", ""))
    return list(entities)


class BM25SparseIndex:
    """
    Okapi BM25 sparse lexical retrieval index (k1=1.5, b=0.75).
    Complements dense semantic vectors by catching exact SKU codes, clause IDs,
    percentages, and supplier names that dense embeddings can blur.
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self._docs: List[Dict[str, Any]] = []
        self._doc_tokens: List[List[str]] = []
        self._doc_term_freqs: List[Counter] = []
        self._doc_lengths: List[int] = []
        self._df: Counter = Counter()
        self._avgdl: float = 0.0
        self._doc_key_to_idx: Dict[str, int] = {}

    def clear(self):
        self._docs.clear()
        self._doc_tokens.clear()
        self._doc_term_freqs.clear()
        self._doc_lengths.clear()
        self._df.clear()
        self._avgdl = 0.0
        self._doc_key_to_idx.clear()

    @property
    def size(self) -> int:
        return len(self._docs)

    def _chunk_key(self, payload: Dict[str, Any]) -> str:
        return f"{payload.get('doc_id', '')}::{payload.get('chunk_index', 0)}::{payload.get('page_number', 1)}"

    def add_documents(self, payloads: List[Dict[str, Any]]) -> None:
        """
        Adds or updates chunk payloads in the BM25 index and recomputes corpus stats.
        """
        for payload in payloads:
            key = self._chunk_key(payload)
            content = payload.get("content", "")
            # Include title and supplier name in lexical index for stronger vendor/document matching
            searchable_text = f"{payload.get('doc_title', '')} {payload.get('supplier_name', '')} {content}"
            tokens = tokenize_legal(searchable_text)
            tf = Counter(tokens)

            if key in self._doc_key_to_idx:
                idx = self._doc_key_to_idx[key]
                old_tf = self._doc_term_freqs[idx]
                for term in old_tf.keys():
                    self._df[term] -= 1
                    if self._df[term] <= 0:
                        del self._df[term]
                self._docs[idx] = payload
                self._doc_tokens[idx] = tokens
                self._doc_term_freqs[idx] = tf
                self._doc_lengths[idx] = len(tokens)
            else:
                idx = len(self._docs)
                self._doc_key_to_idx[key] = idx
                self._docs.append(payload)
                self._doc_tokens.append(tokens)
                self._doc_term_freqs.append(tf)
                self._doc_lengths.append(len(tokens))

            for term in tf.keys():
                self._df[term] += 1

        total_len = sum(self._doc_lengths)
        self._avgdl = (total_len / len(self._docs)) if self._docs else 0.0

    def search(
        self,
        query: str,
        top_k: int = 20,
        supplier_id: Optional[str] = None,
        doc_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        if not self._docs or not query:
            return []

        q_tokens = tokenize_legal(query)
        if not q_tokens:
            return []

        n_docs = len(self._docs)
        avgdl = self._avgdl if self._avgdl > 0 else 1.0
        scored: List[Tuple[float, Dict[str, Any]]] = []

        for idx, payload in enumerate(self._docs):
            if supplier_id and payload.get("supplier_id") != supplier_id:
                continue
            if doc_type and payload.get("doc_type") != doc_type:
                continue

            tf_map = self._doc_term_freqs[idx]
            dl = self._doc_lengths[idx]
            score = 0.0

            for term in q_tokens:
                tf = tf_map.get(term, 0)
                if tf == 0:
                    continue
                df = self._df.get(term, 0)
                # Standard Robertson-Sparck Jones IDF with +1 smoothing so score is always >= 0
                idf = math.log(1.0 + (n_docs - df + 0.5) / (df + 0.5))
                denom = tf + self.k1 * (1.0 - self.b + self.b * (dl / avgdl))
                score += idf * ((tf * (self.k1 + 1.0)) / denom)

            if score > 0.0:
                scored.append((score, payload))

        scored.sort(key=lambda pair: pair[0], reverse=True)
        results = []
        for raw_score, payload in scored[:top_k]:
            results.append({
                "doc_id": payload.get("doc_id", ""),
                "doc_title": payload.get("doc_title", "Document"),
                "supplier_id": payload.get("supplier_id"),
                "supplier_name": payload.get("supplier_name", "Unknown Supplier"),
                "page_number": payload.get("page_number", 1),
                "chunk_index": payload.get("chunk_index", 0),
                "content": payload.get("content", ""),
                "doc_type": payload.get("doc_type", "contract"),
                "bm25_score": round(float(raw_score), 4),
                "score": round(float(raw_score), 4),
            })
        return results


class HybridRRFReranker:
    """
    Reciprocal Rank Fusion (RRF) + Second-Stage Calibrated Lexical-Semantic Cross-Reranker.
    Fuses Dense (BGE/Qdrant) and Sparse (Okapi BM25) ranked lists, then reranks
    candidates using exact entity overlap, bigram proximity, and calibrated score blending.
    """

    def __init__(self, rrf_k: int = 60, dense_weight: float = 0.6, bm25_weight: float = 0.4):
        self.rrf_k = rrf_k
        self.dense_weight = dense_weight
        self.bm25_weight = bm25_weight

    @staticmethod
    def _item_key(item: Dict[str, Any]) -> str:
        # Use doc_id + page + content prefix for deduplication across dense & sparse legs
        return f"{item.get('doc_id', '')}::{item.get('page_number', 1)}::{item.get('content', '')[:80]}"

    def fuse_and_rerank(
        self,
        query: str,
        dense_results: List[Dict[str, Any]],
        bm25_results: List[Dict[str, Any]],
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        candidates: Dict[str, Dict[str, Any]] = {}

        # 1. Process Dense Ranked List
        max_dense = max((r.get("score", 0.0) for r in dense_results), default=1.0) or 1.0
        for rank, item in enumerate(dense_results, start=1):
            key = self._item_key(item)
            rrf_contrib = self.dense_weight / (self.rrf_k + rank)
            candidates[key] = {
                **item,
                "dense_score": round(float(item.get("score", 0.0)), 4),
                "dense_norm": float(item.get("score", 0.0)) / max_dense,
                "bm25_score": 0.0,
                "bm25_norm": 0.0,
                "rrf_score": rrf_contrib,
            }

        # 2. Process Sparse BM25 Ranked List
        max_bm25 = max((r.get("bm25_score", r.get("score", 0.0)) for r in bm25_results), default=1.0) or 1.0
        for rank, item in enumerate(bm25_results, start=1):
            key = self._item_key(item)
            raw_bm25 = float(item.get("bm25_score", item.get("score", 0.0)))
            rrf_contrib = self.bm25_weight / (self.rrf_k + rank)

            if key in candidates:
                candidates[key]["bm25_score"] = round(raw_bm25, 4)
                candidates[key]["bm25_norm"] = raw_bm25 / max_bm25
                candidates[key]["rrf_score"] += rrf_contrib
            else:
                candidates[key] = {
                    **item,
                    "dense_score": 0.0,
                    "dense_norm": 0.0,
                    "bm25_score": round(raw_bm25, 4),
                    "bm25_norm": raw_bm25 / max_bm25,
                    "rrf_score": rrf_contrib,
                }

        if not candidates:
            return []

        # 3. Second-Stage Calibrated Cross-Reranker
        q_tokens = tokenize_legal(query)
        q_set = set(q_tokens)
        q_bigrams = set(zip(q_tokens, q_tokens[1:])) if len(q_tokens) >= 2 else set()
        q_entities = extract_high_value_entities(query)

        max_rrf = max((c["rrf_score"] for c in candidates.values()), default=1.0) or 1.0
        reranked: List[Dict[str, Any]] = []

        for cand in candidates.values():
            doc_text = f"{cand.get('doc_title', '')} {cand.get('supplier_name', '')} {cand.get('content', '')}"
            d_tokens = tokenize_legal(doc_text)
            d_set = set(d_tokens)
            d_bigrams = set(zip(d_tokens, d_tokens[1:])) if len(d_tokens) >= 2 else set()

            # Lexical token coverage (how many distinct query concepts appear in chunk)
            token_coverage = (len(q_set & d_set) / len(q_set)) if q_set else 0.0
            # Phrase / bigram proximity match
            bigram_overlap = (len(q_bigrams & d_bigrams) / len(q_bigrams)) if q_bigrams else 0.0
            # High-value exact legal/SKU entity match (e.g., SKU-LENS-4K, 12.5%, ISO Class 5)
            doc_lower = doc_text.lower().replace(",", "")
            entity_hits = sum(1 for ent in q_entities if ent in doc_lower)
            entity_boost = (entity_hits / len(q_entities)) if q_entities else 0.0

            rrf_norm = cand["rrf_score"] / max_rrf

            # Weighted cross-feature rerank score bounded cleanly in [0, 1]
            rerank_score = (
                0.35 * rrf_norm
                + 0.25 * cand["dense_norm"]
                + 0.15 * cand["bm25_norm"]
                + 0.10 * token_coverage
                + 0.05 * bigram_overlap
                + 0.10 * entity_boost
            )
            if entity_hits > 0:
                rerank_score = min(1.0, rerank_score + 0.12 * entity_boost)

            result_item = {
                "doc_id": cand.get("doc_id", ""),
                "doc_title": cand.get("doc_title", "Document"),
                "supplier_id": cand.get("supplier_id"),
                "supplier_name": cand.get("supplier_name", "Unknown Supplier"),
                "page_number": cand.get("page_number", 1),
                "content": cand.get("content", ""),
                "doc_type": cand.get("doc_type", "contract"),
                "score": round(float(rerank_score), 4),
                "dense_score": cand["dense_score"],
                "bm25_score": cand["bm25_score"],
                "rrf_score": round(float(cand["rrf_score"]), 5),
                "retrieval_method": "hybrid_rrf_reranked",
            }
            reranked.append(result_item)

        reranked.sort(key=lambda x: (x["score"], x["rrf_score"], x["dense_score"]), reverse=True)
        return reranked[:top_k]
