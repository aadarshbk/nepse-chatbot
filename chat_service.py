from typing import Dict, Any

from analysis import get_market_data
from ai_service import get_trade_signal

BOT_NAME = "TradeMind"


def generate_bot_reply(message: str, symbol: str = "BOKL") -> Dict[str, Any]:
    """
    Core bot logic used by both HTML and JSON chat endpoints.

    :param message: User's message/question.
    :param symbol: Stock symbol to analyze (default: BOKL).
    :return: Structured bot reply with signal, confidence, reasoning, and market data.
    """
    market_data = get_market_data(symbol)
    ai_result = get_trade_signal(symbol, market_data, message)

    signal = ai_result.get("signal", "UNKNOWN")
    confidence = ai_result.get("confidence", "0%")
    reasoning = ai_result.get("reasoning", "No reasoning provided.")

    return {
        "bot_name": BOT_NAME,
        "symbol": symbol,
        "signal": signal,
        "confidence": confidence,
        "reasoning": reasoning,
        "market": {
            "summary": market_data.get("summary"),
            "trend": market_data.get("trend", "Unknown"),
        },
    }


