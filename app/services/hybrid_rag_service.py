"""Hybrid RAG Service combining dense (semantic) and sparse (keyword) retrieval."""
import logging
import numpy as np
from typing import Any
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer, util
import threading

logger = logging.getLogger(__name__)

# Load knowledge base - shared between instances
from app.services.knowledge_service import KNOWLEDGE_BASE
from app.services.rag_optimizer import get_optimizer


class HybridRAGService:
    """
    Hybrid RAG service that combines:
    1. Dense retrieval (semantic search using embeddings)
    2. Sparse retrieval (BM25 keyword matching)
    3. Reranking with weighted scores
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", cache_embeddings: bool = True):
        """
        Initialize hybrid RAG service.

        Args:
            model_name: Hugging Face model for embeddings (lightweight model)
            cache_embeddings: Whether to cache embeddings
        """
        self.model_name = model_name
        self.cache_embeddings = cache_embeddings
        self._lock = threading.Lock()
        self._initialized = False
        self._embedder = None
        self._bm25 = None
        self._documents = []
        self._embeddings = {}
        self._kb_index = {}  # Map doc_id to KB entry

        # Lazy initialization
        self._init_lock = threading.Lock()

    def _initialize(self):
        """Initialize embedder and prepare knowledge base (lazy initialization)."""
        if self._initialized:
            return

        with self._init_lock:
            if self._initialized:
                return

            try:
                logger.info(f"Loading embedding model: {self.model_name}")
                self._embedder = SentenceTransformer(self.model_name)

                self._prepare_knowledge_base()
                self._initialized = True
                logger.info("Hybrid RAG service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Hybrid RAG: {e}")
                raise

    def _prepare_knowledge_base(self):
        """Prepare knowledge base documents and embeddings."""
        self._documents = []
        self._embeddings = {}
        self._kb_index = {}

        for idx, kb_entry in enumerate(KNOWLEDGE_BASE):
            doc_id = f"kb_{idx}"
            # Combine title, summary, and detail for richer context
            combined_text = (
                f"{kb_entry.get('title', '')}. "
                f"{kb_entry.get('summary', '')}. "
                f"{kb_entry.get('detail', '')}"
            )
            self._documents.append(combined_text)
            self._kb_index[doc_id] = kb_entry

        if self._documents:
            logger.info(f"Loaded {len(self._documents)} documents from knowledge base")
            
            # Create embeddings
            if self.cache_embeddings:
                logger.info("Creating and caching embeddings...")
                embeddings = self._embedder.encode(
                    self._documents, convert_to_tensor=True, show_progress_bar=False
                )
                self._embeddings = {f"kb_{i}": emb for i, emb in enumerate(embeddings)}
                logger.info(f"Cached {len(self._embeddings)} embeddings")

            # Initialize BM25
            # Tokenize for BM25 (split by spaces and punctuation)
            tokenized_docs = [doc.lower().split() for doc in self._documents]
            self._bm25 = BM25Okapi(tokenized_docs)
            logger.info("BM25 index initialized")

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        dense_weight: float = 0.7,
        sparse_weight: float = 0.3,
        threshold: float = 0.3,
        optimize: bool = True,
    ) -> list[dict[str, Any]]:
        """
        Retrieve relevant documents using hybrid approach with optional optimization.

        Args:
            query: Search query
            top_k: Number of top results to return
            dense_weight: Weight for semantic search (0-1)
            sparse_weight: Weight for BM25 search (0-1)
            threshold: Minimum relevance score (0-1)
            optimize: Apply optimization techniques to results

        Returns:
            List of documents with relevance scores, sorted by score
        """
        if not self._initialized:
            self._initialize()

        if not query or not query.strip():
            logger.warning("Empty query provided")
            return []

        try:
            # 1. Dense retrieval (semantic search)
            dense_scores = self._dense_retrieve(query, top_k * 2)

            # 2. Sparse retrieval (BM25)
            sparse_scores = self._sparse_retrieve(query, top_k * 2)

            # 3. Combine and rerank
            combined = self._combine_results(
                dense_scores, sparse_scores, dense_weight, sparse_weight, threshold
            )

            # 4. Sort by score
            combined = sorted(combined, key=lambda x: x["score"], reverse=True)[:top_k * 2]

            # 5. Apply optimization if enabled
            if optimize:
                optimizer = get_optimizer()
                combined = optimizer.optimize_retrieval(query, combined)

            # 6. Return top_k
            results = combined[:top_k]
            logger.info(f"Retrieved {len(results)} results for query: {query[:50]}")
            return results

        except Exception as e:
            logger.error(f"Error in hybrid retrieval: {e}")
            return []

    def _dense_retrieve(self, query: str, top_k: int) -> dict[str, float]:
        """
        Semantic search using embeddings.

        Returns:
            Dict mapping doc_id to similarity score
        """
        try:
            query_embedding = self._embedder.encode(query, convert_to_tensor=True)
            scores = {}

            for doc_id, doc_embedding in self._embeddings.items():
                similarity = util.pytorch_cos_sim(query_embedding, doc_embedding).item()
                scores[doc_id] = float(similarity)

            # Return top_k by score
            top_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
            return dict(top_scores)

        except Exception as e:
            logger.error(f"Error in dense retrieval: {e}")
            return {}

    def _sparse_retrieve(self, query: str, top_k: int) -> dict[str, float]:
        """
        Keyword search using BM25.

        Returns:
            Dict mapping doc_id to BM25 score (normalized to 0-1)
        """
        try:
            query_tokens = query.lower().split()
            bm25_scores = self._bm25.get_scores(query_tokens)

            # Normalize scores to 0-1 range
            max_score = max(bm25_scores) if bm25_scores.size > 0 else 1
            normalized_scores = {}

            for idx, score in enumerate(bm25_scores):
                doc_id = f"kb_{idx}"
                normalized_score = float(score / max_score) if max_score > 0 else 0.0
                normalized_scores[doc_id] = normalized_score

            # Return top_k
            top_scores = sorted(normalized_scores.items(), key=lambda x: x[1], reverse=True)[
                :top_k
            ]
            return dict(top_scores)

        except Exception as e:
            logger.error(f"Error in sparse retrieval: {e}")
            return {}

    def _combine_results(
        self,
        dense_scores: dict[str, float],
        sparse_scores: dict[str, float],
        dense_weight: float,
        sparse_weight: float,
        threshold: float,
    ) -> list[dict[str, Any]]:
        """
        Combine dense and sparse retrieval results with weighted scoring.

        Returns:
            List of documents with combined scores
        """
        all_doc_ids = set(dense_scores.keys()) | set(sparse_scores.keys())
        results = []

        for doc_id in all_doc_ids:
            dense_score = dense_scores.get(doc_id, 0.0)
            sparse_score = sparse_scores.get(doc_id, 0.0)

            # Weighted combination
            combined_score = (dense_weight * dense_score) + (sparse_weight * sparse_score)

            # Apply threshold
            if combined_score >= threshold:
                kb_entry = self._kb_index.get(doc_id, {})
                results.append(
                    {
                        "doc_id": doc_id,
                        "score": combined_score,
                        "dense_score": dense_score,
                        "sparse_score": sparse_score,
                        "content": kb_entry.get("detail", ""),
                        "title": kb_entry.get("title", ""),
                        "summary": kb_entry.get("summary", ""),
                    }
                )

        return results

    def format_context(
        self, results: list[dict[str, Any]], max_length: int = 2000
    ) -> str:
        """
        Format retrieved results into readable context.

        Args:
            results: Retrieved documents
            max_length: Maximum length of context string

        Returns:
            Formatted context string
        """
        if not results:
            return "No relevant knowledge base entries found."

        lines = ["RELEVANT NEPSE KNOWLEDGE:"]
        current_length = len(lines[0])

        for result in results:
            title = result.get("title", "")
            content = result.get("content", "")
            score = result.get("score", 0)

            # Create entry
            entry = f"- {title}: {content}"

            # Check length
            if current_length + len(entry) > max_length:
                break

            lines.append(entry)
            current_length += len(entry)

        return "\n".join(lines)


# Global instance (singleton)
_hybrid_rag_service = None
_rag_lock = threading.Lock()


def get_hybrid_rag_service() -> HybridRAGService:
    """Get or create global hybrid RAG service instance."""
    global _hybrid_rag_service
    if _hybrid_rag_service is None:
        with _rag_lock:
            if _hybrid_rag_service is None:
                _hybrid_rag_service = HybridRAGService()
    return _hybrid_rag_service


def retrieve_hybrid_context(
    query: str, top_k: int = 5, dense_weight: float = 0.7, sparse_weight: float = 0.3
) -> str:
    """
    Convenience function to retrieve and format context using hybrid RAG.

    Args:
        query: Search query
        top_k: Number of results
        dense_weight: Weight for semantic search
        sparse_weight: Weight for keyword search

    Returns:
        Formatted context string
    """
    service = get_hybrid_rag_service()
    results = service.retrieve(query, top_k, dense_weight, sparse_weight)
    return service.format_context(results)
