"""Chat service for bot interactions."""
import logging
from typing import Any

from app.services.analysis_service import get_market_data
from app.services.ai_service import get_trade_signal
from app.services.hybrid_rag_service import retrieve_hybrid_context
from app.utils import get_symbol_sector, strip_markdown
from app.core import settings

logger = logging.getLogger(__name__)


def _format_market_context(symbol: str, market_data: dict) -> str:
    """Format market data into readable context for AI."""
    if not market_data or market_data.get("error"):
        return f"No market data available for {symbol}. Answer from general NEPSE knowledge."

    sector    = get_symbol_sector(symbol)
    field_map = [
        ("ltp",     "LTP"),
        ("change",  "Change today"),
        ("high",    "52-week High"),
        ("low",     "52-week Low"),
        ("volume",  "Volume"),
        ("trend",   "Trend"),
        ("rsi",     "RSI"),
        ("sma20",   "SMA20"),
        ("sma50",   "SMA50"),
        ("summary", "Summary"),
    ]
    lines = [f"Stock : {symbol}  ({sector})"]
    for key, label in field_map:
        value = market_data.get(key)
        if value is not None:
            lines.append(f"{label:<16}: {value}")
    return "\n".join(lines)


def generate_bot_reply(
    message: str,
    symbol: str = "NABIL",
    history: list[dict] | None = None,
) -> dict[str, Any]:
    """Generate a bot reply for user message using hybrid RAG."""
    
    # Step 1: Fetch market data
    market_data: dict = {}
    try:
        market_data = get_market_data(symbol) or {}
    except Exception as e:
        logger.warning(f"Market data unavailable for {symbol}: {e}")

    # Step 2: Build context for AI
    market_context = _format_market_context(symbol, market_data)

    # Step 2b: Use hybrid RAG to get relevant knowledge
    try:
        # Retrieve with hybrid approach (semantic + keyword search)
        kb_context = retrieve_hybrid_context(
            message, 
            top_k=5,
            dense_weight=0.7,  # 70% weight on semantic similarity
            sparse_weight=0.3  # 30% weight on keyword matching
        )
        if kb_context:
            market_context += f"\n\n{kb_context}"
    except Exception as e:
        logger.warning(f"Hybrid RAG retrieval failed: {e}")
        # Gracefully degrade - could fall back to old method here if needed

    # Step 3: Call the AI
    reasoning = ""
    try:
        reasoning = get_trade_signal(
            message=message,
            history=history,
            market_context=market_context,
        )
        reasoning = strip_markdown(reasoning)
    except RuntimeError as e:
        reasoning = str(e)
    except Exception as e:
        logger.error(f"Unexpected AI error: {e}")
        reasoning = "Sorry, I encountered an unexpected error. Please try again."

    # Step 4: Return structured response
    return {
        "bot_name":  settings.bot_name,
        "symbol":    symbol,
        "reasoning": reasoning,
        "market": {
            "summary": market_data.get("summary"),
            "trend": market_data.get("trend"),
        },
    }
