# chat_service.py
import re
import logging
from typing import Any

from analysis import get_market_data
from ai_service import get_trade_signal
from utils import get_symbol_sector
from knowledge_base import get_context_for_query

logger   = logging.getLogger(__name__)
BOT_NAME = "TradeMind"


def _strip_markdown(text: str) -> str:
    """
    Remove all markdown formatting from AI responses so they
    display as clean plain text in the browser.

    Handles: **bold**, *italic*, # headers, ``` code blocks, `inline code`
    """
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)  # fenced code blocks
    text = re.sub(r'`(.+?)`',   r'\1', text)                # inline code
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)            # **bold**
    text = re.sub(r'\*(.+?)\*',     r'\1', text)            # *italic*
    text = re.sub(r'__(.+?)__',     r'\1', text)            # __bold__
    text = re.sub(r'_(.+?)_',       r'\1', text)            # _italic_
    text = re.sub(r'#{1,6}\s*',     '',    text)            # ## headings
    text = re.sub(r'\n{3,}', '\n\n', text)                  # collapse extra blank lines
    return text.strip()


def _format_market_context(symbol: str, market_data: dict) -> str:
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

    # Step 1: Fetch market data
    market_data: dict = {}
    try:
        market_data = get_market_data(symbol) or {}
    except Exception as e:
        logger.warning(f"Market data unavailable for {symbol}: {e}")

    # Step 2: Build context for AI
    market_context = _format_market_context(symbol, market_data)

    # Step 2b: Append relevant knowledge base entries
    kb_context = get_context_for_query(message)
    if kb_context:
        market_context += f"\n\nRELEVANT NEPSE KNOWLEDGE:\n{kb_context}"

    # Step 3: Call the AI
    reasoning = ""
    try:
        reasoning = get_trade_signal(
            message=message,
            history=history,
            market_context=market_context,
        )
        reasoning = _strip_markdown(reasoning)
    except RuntimeError as e:
        reasoning = str(e)
    except Exception as e:
        logger.error(f"Unexpected AI error: {e}")
        reasoning = "Sorry, I encountered an unexpected error. Please try again."

    # Step 4: Return structured response
    return {
        "bot_name":  BOT_NAME,
        "symbol":    symbol,
        "reasoning": reasoning,
        "market": {
            "summary": market_data.get("summary"),
            "trend":   market_data.get("trend", "unknown"),
            "ltp":     market_data.get("ltp"),
        },
    }