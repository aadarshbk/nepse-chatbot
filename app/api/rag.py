"""Advanced RAG API endpoints for hybrid retrieval."""
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from typing import Any
import logging

from app.services.hybrid_rag_service import get_hybrid_rag_service
from app.services.rag_optimizer import get_optimizer

logger = logging.getLogger(__name__)

rag_router = APIRouter(prefix="/api/rag", tags=["RAG"])


class RAGQueryRequest(BaseModel):
    """Request for RAG retrieval."""

    query: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(default=5, ge=1, le=20)
    dense_weight: float = Field(default=0.7, ge=0, le=1)
    sparse_weight: float = Field(default=0.3, ge=0, le=1)
    threshold: float = Field(default=0.3, ge=0, le=1)
    optimize: bool = Field(default=True)


class RAGResult(BaseModel):
    """Single RAG result."""

    title: str
    summary: str
    content: str
    score: float
    dense_score: float
    sparse_score: float


class RAGResponse(BaseModel):
    """Response from RAG retrieval."""

    query: str
    results: list[RAGResult]
    total_results: int
    optimization_applied: bool = False


class DebugRAGResponse(BaseModel):
    """Debug response with detailed metrics."""

    query: str
    results: list[dict[str, Any]]
    dense_results: list[dict[str, Any]]
    sparse_results: list[dict[str, Any]]
    combined_results: list[dict[str, Any]]
    final_results: list[dict[str, Any]]


@rag_router.post("/retrieve", response_model=RAGResponse)
async def retrieve_rag(request: RAGQueryRequest) -> RAGResponse:
    """
    Retrieve documents using hybrid RAG.

    Args:
        request: RAG query request

    Returns:
        Retrieved results with scores
    """
    try:
        service = get_hybrid_rag_service()

        # Retrieve results
        results = service.retrieve(
            query=request.query,
            top_k=request.top_k,
            dense_weight=request.dense_weight,
            sparse_weight=request.sparse_weight,
            threshold=request.threshold,
            optimize=request.optimize,
        )

        # Convert to response format
        rag_results = [
            RAGResult(
                title=r.get("title", ""),
                summary=r.get("summary", ""),
                content=r.get("content", ""),
                score=r.get("score", 0),
                dense_score=r.get("dense_score", 0),
                sparse_score=r.get("sparse_score", 0),
            )
            for r in results
        ]

        return RAGResponse(
            query=request.query,
            results=rag_results,
            total_results=len(rag_results),
            optimization_applied=request.optimize,
        )

    except Exception as e:
        logger.error(f"RAG retrieval error: {e}")
        return RAGResponse(
            query=request.query, results=[], total_results=0, optimization_applied=False
        )


@rag_router.get("/health")
async def rag_health():
    """Check RAG service health."""
    try:
        service = get_hybrid_rag_service()
        return {
            "status": "healthy",
            "initialized": service._initialized,
            "model": service.model_name,
            "documents_count": len(service._documents),
        }
    except Exception as e:
        logger.error(f"RAG health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}


@rag_router.post("/analyze-intent")
async def analyze_intent(query: str = Query(..., min_length=1)):
    """
    Analyze query intent for debugging.

    Args:
        query: User query

    Returns:
        Detected intents
    """
    try:
        optimizer = get_optimizer()
        intents = optimizer.context_analyzer.detect_intent(query)
        return {"query": query, "intents": intents}
    except Exception as e:
        logger.error(f"Intent analysis error: {e}")
        return {"query": query, "intents": [], "error": str(e)}


@rag_router.post("/expand-query")
async def expand_query(query: str = Query(..., min_length=1)):
    """
    Expand query with synonyms for debugging.

    Args:
        query: User query

    Returns:
        Expanded queries
    """
    try:
        from app.services.rag_optimizer import QueryExpander

        expanded = QueryExpander.expand_query(query, max_expansions=3)
        return {"original_query": query, "expanded_queries": expanded}
    except Exception as e:
        logger.error(f"Query expansion error: {e}")
        return {"original_query": query, "expanded_queries": [], "error": str(e)}


@rag_router.get("/knowledge-base/stats")
async def knowledge_base_stats():
    """Get statistics about the knowledge base."""
    try:
        service = get_hybrid_rag_service()
        if not service._initialized:
            service._initialize()

        return {
            "total_documents": len(service._documents),
            "embedding_model": service.model_name,
            "embeddings_cached": len(service._embeddings),
            "cache_enabled": service.cache_embeddings,
        }
    except Exception as e:
        logger.error(f"KB stats error: {e}")
        return {"error": str(e)}
