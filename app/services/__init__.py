"""Services package."""
from app.services.nepse_service import nepse_fetcher
from app.services.ai_service import ai_service, get_trade_signal
from app.services.analysis_service import get_market_data
from app.services.knowledge_service import (
    search as knowledge_search,
    get_by_id,
    get_all_topics,
    get_context_for_query,
)
from app.services.chat_service import generate_bot_reply
from app.services.hybrid_rag_service import (
    get_hybrid_rag_service,
    retrieve_hybrid_context,
    HybridRAGService,
)

__all__ = [
    "nepse_fetcher",
    "ai_service",
    "get_trade_signal",
    "get_market_data",
    "knowledge_search",
    "get_by_id",
    "get_all_topics",
    "get_context_for_query",
    "generate_bot_reply",
    "get_hybrid_rag_service",
    "retrieve_hybrid_context",
    "HybridRAGService",
]
