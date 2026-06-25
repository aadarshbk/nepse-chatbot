"""Configuration for Hybrid RAG service."""
from pydantic_settings import BaseSettings


class RAGConfig(BaseSettings):
    """Hybrid RAG configuration settings."""

    # Model settings
    embedding_model: str = "all-MiniLM-L6-v2"  # Lightweight, fast embedding model
    cache_embeddings: bool = True  # Cache embeddings for performance

    # Retrieval settings
    top_k_results: int = 5  # Default number of results to retrieve
    default_dense_weight: float = 0.7  # Weight for semantic search (0-1)
    default_sparse_weight: float = 0.3  # Weight for keyword search (0-1)
    relevance_threshold: float = 0.3  # Minimum relevance score (0-1)

    # Context formatting
    max_context_length: int = 2000  # Maximum context string length
    include_scores: bool = False  # Include relevance scores in output

    # Performance settings
    batch_size: int = 32  # Batch size for embedding creation
    normalize_scores: bool = True  # Normalize scores to 0-1 range

    # Advanced settings
    use_reranking: bool = True  # Use reranking to improve results
    rerank_top_k: int = 10  # Top K before reranking
    min_similarity: float = 0.1  # Minimum similarity threshold for results

    class Config:
        """Pydantic config."""
        env_prefix = "RAG_"
        case_sensitive = False


# Global RAG config instance
rag_config = RAGConfig()
