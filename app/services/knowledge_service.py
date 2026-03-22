"""Knowledge base service for NEPSE education."""
from __future__ import annotations
import re
import logging

logger = logging.getLogger(__name__)

KNOWLEDGE_BASE: list[dict] = [
    {
        "id": "market_hours", "title": "Market Hours",
        "summary": "NEPSE trades Sunday–Thursday, 11:00 AM – 3:00 PM NST.",
        "detail": (
            "NEPSE is open Sunday through Thursday, 11:00 AM to 3:00 PM Nepal Standard Time (NST). "
            "Friday and Saturday are the weekend in Nepal — market is closed. "
            "NST is UTC+5:45. Orders outside trading hours queue for the next session."
        ),
        "tags": ["hours", "trading hours", "open", "closed", "weekend", "sunday", "schedule", "time"],
    },
    {
        "id": "settlement", "title": "T+2 Settlement",
        "summary": "Trades settle 2 business days after execution.",
        "detail": (
            "NEPSE uses T+2 settlement. If you buy shares on Sunday (T), they arrive in your "
            "DEMAT account on Tuesday (T+2). Cash from a sale also arrives on T+2. "
            "Weekends and holidays are not counted. You cannot reuse sale proceeds immediately."
        ),
        "tags": ["settlement", "t+2", "demat", "clearing", "delivery", "days"],
    },
    {
        "id": "circuit_breaker", "title": "Circuit Breaker (±10%)",
        "summary": "Trading halts if a stock moves more than 10% in one day.",
        "detail": (
            "NEPSE circuit breaker rule: a stock cannot move more than ±10% from its previous close. "
            "Upper circuit (+10%): strong demand, buyers may find no sellers. "
            "Lower circuit (-10%): heavy selling, sellers may find no buyers. "
            "This protects against extreme volatility and panic."
        ),
        "tags": ["circuit", "circuit breaker", "limit", "10%", "upper circuit", "lower circuit", "halt"],
    },
    {
        "id": "nepse_index", "title": "NEPSE Index",
        "summary": "Measures overall performance of all listed stocks.",
        "detail": (
            "The NEPSE index is a market-cap-weighted index tracking all listed stocks. "
            "Rising index = overall market gaining. Falling = overall market declining. "
            "Sector sub-indices exist for banking, hydropower, insurance etc."
        ),
        "tags": ["nepse", "index", "market", "overall", "benchmark", "performance"],
    },
    {
        "id": "capital_gains_tax", "title": "Capital Gains Tax",
        "summary": "5% if held over 1 year; 7.5% if held 1 year or less.",
        "detail": (
            "Capital Gains Tax (CGT) on share profits in Nepal: "
            "Long-term (>1 year): 5%. Short-term (≤1 year): 7.5%. "
            "Profit = Sale Price − Purchase Price − Brokerage Fees. "
            "Tax is deducted at source by your broker automatically."
        ),
        "tags": ["tax", "capital gains", "cgt", "profit", "sell", "short term", "long term", "5%", "7.5%"],
    },
    {
        "id": "dividend_tax", "title": "Dividend Tax",
        "summary": "5% on cash dividends; 7.5% on bonus shares.",
        "detail": (
            "Cash dividend: taxed at 5%, deducted before you receive payment. "
            "Bonus shares: taxed at 7.5%. Bonus shares increase kitta held but may dilute price. "
            "Example: 10% cash dividend on Rs.100 face value = Rs.10 per kitta, you receive Rs.9.50 after tax."
        ),
        "tags": ["tax", "dividend", "bonus shares", "cash dividend", "5%", "7.5%", "income"],
    },
    {
        "id": "kitta", "title": "Kitta",
        "summary": "Kitta = one unit (one share) of a company.",
        "detail": (
            "Kitta is the Nepali term for a single share unit. "
            "'I bought 50 kitta of NABIL' = 50 shares of NABIL Bank. "
            "Minimum trade quantity is 1 kitta. Face value of most NEPSE shares is Rs.100 per kitta."
        ),
        "tags": ["kitta", "share", "unit", "quantity", "lot"],
    },
    {
        "id": "ltp", "title": "LTP (Last Traded Price)",
        "summary": "The most recent price at which a stock was traded.",
        "detail": (
            "LTP = Last Traded Price — the price of the most recent transaction. "
            "It updates every time a new trade occurs during market hours. "
            "After market close, LTP freezes at the day's final traded price. "
            "LTP is NOT face value — a Rs.100 face-value share may trade at Rs.1,200 LTP."
        ),
        "tags": ["ltp", "last traded price", "price", "current price", "market price"],
    },
    {
        "id": "rsi", "title": "RSI (Relative Strength Index)",
        "summary": "Momentum indicator: above 70 = overbought, below 30 = oversold.",
        "detail": (
            "RSI ranges 0–100 and measures price momentum. "
            "RSI > 70: overbought — sharp rise, pullback may occur. "
            "RSI < 30: oversold — sharp fall, bounce may occur. "
            "RSI 40–60: neutral zone. "
            "RSI is a signal, not a guarantee — a stock can stay overbought in a strong trend."
        ),
        "tags": ["rsi", "relative strength", "overbought", "oversold", "momentum", "indicator"],
    },
    {
        "id": "sma", "title": "SMA (Simple Moving Average)",
        "summary": "Average closing price over N days — smooths out noise.",
        "detail": (
            "SMA = average closing price over a period (e.g. SMA20 = last 20 days). "
            "Price above SMA20: short-term uptrend. Price below: downtrend."
        ),
        "tags": ["sma", "moving average", "average", "trend", "sma20", "sma50"],
    },
    {
        "id": "pe_ratio", "title": "P/E Ratio",
        "summary": "How much you pay per rupee of company profit.",
        "detail": (
            "P/E = LTP ÷ EPS. Low P/E vs sector avg: potentially undervalued. "
            "High P/E: growth expected or overvalued. Always compare within the same sector."
        ),
        "tags": ["pe ratio", "p/e", "price to earnings", "eps", "valuation"],
    },
]


def search(query: str, max_results: int = 3) -> list[dict]:
    """Search knowledge base for relevant entries."""
    if not query or not query.strip():
        return []
    keywords = re.findall(r'\w+', query.lower())
    scored: list[tuple[int, dict]] = []
    for entry in KNOWLEDGE_BASE:
        score = 0
        searchable = " ".join([
            entry.get("title", ""), entry.get("summary", ""),
            entry.get("detail", ""), " ".join(entry.get("tags", [])),
        ]).lower()
        for kw in keywords:
            if kw in searchable:
                if kw in [t.lower() for t in entry.get("tags", [])]:
                    score += 3
                elif kw in entry.get("title", "").lower():
                    score += 2
                else:
                    score += 1
        if score > 0:
            scored.append((score, entry))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [e for _, e in scored[:max_results]]


def get_by_id(entry_id: str) -> dict | None:
    """Get knowledge base entry by ID."""
    return next((e for e in KNOWLEDGE_BASE if e.get("id") == entry_id), None)


def get_all_topics() -> list[dict]:
    """Get list of all knowledge base topics."""
    return [{"id": e["id"], "title": e["title"], "summary": e["summary"]} for e in KNOWLEDGE_BASE]


def format_for_ai(entries: list[dict]) -> str:
    """Format knowledge entries for AI context."""
    if not entries:
        return ""
    return "\n\n".join(
        f"## {e['title']}\n{e['summary']}\n{e['detail']}" for e in entries
    )


def get_context_for_query(query: str) -> str:
    """Get formatted context for AI based on query."""
    return format_for_ai(search(query, max_results=2))
