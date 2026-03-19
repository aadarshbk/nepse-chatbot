# knowledge_base.py
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
        "id": "broker_commission", "title": "Broker Commission",
        "summary": "Charged on every buy and sell — factor this into profit calculations.",
        "detail": (
            "NEPSE broker commission rates: "
            "Up to Rs.50,000: 0.40% | Rs.50k–500k: 0.37% | Rs.500k–2M: 0.34% | Above Rs.2M: 0.30%. "
            "Commission applies to both buy and sell sides. SEBON service charge: 0.015%. "
            "Always factor both commissions before calculating break-even."
        ),
        "tags": ["commission", "broker", "fee", "cost", "brokerage", "sebon", "transaction cost"],
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
        "id": "rights_offering", "title": "Rights Offering (RO)",
        "summary": "Company offers existing shareholders new shares at a discount.",
        "detail": (
            "A Rights Offering lets existing shareholders buy new shares at a discounted price, "
            "usually at or near face value (Rs.100), even if LTP is much higher. "
            "Example: 1:10 RO means for every 10 kitta you own, you can buy 1 new kitta at Rs.100. "
            "Rights can be exercised or sold in the secondary market. "
            "LTP typically adjusts downward after rights issue (dilution effect)."
        ),
        "tags": ["rights", "ro", "rights offering", "issue", "new shares", "discount", "dilution"],
    },
    {
        "id": "ipo", "title": "IPO (Initial Public Offering)",
        "summary": "When a company lists on NEPSE for the first time.",
        "detail": (
            "IPO = first-time public share sale by a company on NEPSE. "
            "Applied through MeroShare. Allotted via lottery if oversubscribed. "
            "IPO shares issued at face value (Rs.100). After listing, price often rises (listing gain). "
            "Read the company prospectus before applying — not all IPOs gain."
        ),
        "tags": ["ipo", "initial public offering", "listing", "meroshare", "apply", "allotment", "lottery"],
    },
    {
        "id": "demat", "title": "DEMAT Account",
        "summary": "Digital account where your shares are held electronically.",
        "detail": (
            "DEMAT (dematerialised) account stores your shares electronically via CDSC. "
            "Required to buy/sell on NEPSE. Open at any CDSC-registered bank. "
            "Shares appear after T+2 settlement. Check holdings on MeroShare."
        ),
        "tags": ["demat", "account", "cdsc", "meroshare", "holdings", "electronic", "open account"],
    },
    {
        "id": "meroshare", "title": "MeroShare",
        "summary": "Official CDSC platform to apply for IPOs and view your holdings.",
        "detail": (
            "MeroShare (meroshare.cdsc.com.np) is the official investor platform by CDSC. "
            "Use it to: apply for IPOs/FPOs, view DEMAT balance, check allotment results, "
            "transfer shares, view dividend history. "
            "Requires your DEMAT number and registered mobile to register."
        ),
        "tags": ["meroshare", "cdsc", "ipo apply", "portfolio", "demat", "platform", "online"],
    },
    {
        "id": "rsi", "title": "RSI (Relative Strength Index)",
        "summary": "Momentum indicator: above 70 = overbought, below 30 = oversold.",
        "detail": (
            "RSI ranges 0–100 and measures price momentum. "
            "RSI > 70: overbought — sharp rise, pullback may occur. "
            "RSI < 30: oversold — sharp fall, bounce may occur. "
            "RSI 40–60: neutral zone. "
            "RSI is a signal, not a guarantee — a stock can stay overbought in a strong trend. "
            "Always use alongside other indicators."
        ),
        "tags": ["rsi", "relative strength", "overbought", "oversold", "momentum", "indicator", "technical"],
    },
    {
        "id": "sma", "title": "SMA (Simple Moving Average)",
        "summary": "Average closing price over N days — smooths out noise.",
        "detail": (
            "SMA = average closing price over a period (e.g. SMA20 = last 20 days). "
            "Price above SMA20: short-term uptrend. Price below: downtrend. "
            "SMA20 crosses above SMA50 = Golden Cross (bullish). "
            "SMA20 crosses below SMA50 = Death Cross (bearish). "
            "SMA reacts slowly — better for trends than exact timing."
        ),
        "tags": ["sma", "moving average", "average", "trend", "sma20", "sma50", "golden cross", "death cross"],
    },
    {
        "id": "support_resistance", "title": "Support and Resistance",
        "summary": "Price levels where stocks tend to stop falling or rising.",
        "detail": (
            "Support: price level where stock historically stopped falling and bounced (buyers step in). "
            "Resistance: price level where stock historically stopped rising and pulled back (sellers step in). "
            "When resistance breaks, it often becomes new support — and vice versa."
        ),
        "tags": ["support", "resistance", "price level", "breakout", "bounce", "technical", "chart"],
    },
    {
        "id": "banking_sector", "title": "Banking Sector",
        "summary": "Largest and most liquid sector on NEPSE.",
        "detail": (
            "Banking is NEPSE's largest sector: 27 commercial banks (Class A), development banks (Class B), "
            "finance companies (Class C). "
            "Stocks like NABIL, HBL, EBL are widely held. Sensitive to NRB policy, interest rates, "
            "credit growth, and NPL ratios. High liquidity makes them popular for beginners."
        ),
        "tags": ["bank", "banking", "commercial bank", "nabil", "hbl", "ebl", "class a", "sector"],
    },
    {
        "id": "hydropower_sector", "title": "Hydropower Sector",
        "summary": "High growth potential — long payback periods before revenue.",
        "detail": (
            "Key stocks: UPPER, CHCL, HIDCL, BPCL, API. "
            "Long pre-revenue construction phase. Predictable cash flows once operational. "
            "Sensitive to monsoon and water availability. HIDCL is government-backed. "
            "Can be volatile before projects reach commercial operation."
        ),
        "tags": ["hydro", "hydropower", "upper", "chcl", "hidcl", "bpcl", "energy", "sector"],
    },
    {
        "id": "sebon", "title": "SEBON",
        "summary": "Securities Board of Nepal — regulates Nepal's capital market.",
        "detail": (
            "SEBON regulates NEPSE, brokers, mutual funds, and IPO approvals. "
            "Sets rules for investor protection, transparency, and corporate governance. "
            "File broker or company complaints with SEBON."
        ),
        "tags": ["sebon", "regulator", "securities board", "rules", "regulation", "complaint"],
    },
    {
        "id": "nrb", "title": "NRB (Nepal Rastra Bank)",
        "summary": "Nepal's central bank — policies directly affect banking stocks.",
        "detail": (
            "NRB monetary policy affects NEPSE especially banking stocks. "
            "Key tools: CRR (cash reserve ratio), policy rate, margin lending restrictions. "
            "NRB tightening → stock prices often fall. NRB easing → markets often rally."
        ),
        "tags": ["nrb", "central bank", "nepal rastra bank", "monetary policy", "crr", "interest rate", "liquidity"],
    },
    {
        "id": "face_value", "title": "Face Value",
        "summary": "Nominal share value — usually Rs.100, NOT the market price.",
        "detail": (
            "Face value (par value) is the nominal value defined in the company's Articles — usually Rs.100. "
            "It is NOT the market price (LTP). NABIL face value = Rs.100, LTP may be Rs.1,200. "
            "Used to calculate dividends, rights offering prices, and bonus shares."
        ),
        "tags": ["face value", "par value", "rs 100", "nominal", "dividend calculation"],
    },
    {
        "id": "floor_price", "title": "Floor & Ceiling Price",
        "summary": "Min/max price a stock can trade in one day (±10% of previous close).",
        "detail": (
            "Floor = Previous Close × 0.90. Ceiling = Previous Close × 1.10. "
            "Example: previous close Rs.1,000 → floor Rs.900, ceiling Rs.1,100. "
            "Stock cannot trade outside this band on that day."
        ),
        "tags": ["floor price", "ceiling price", "circuit", "minimum price", "maximum price", "band"],
    },
    {
        "id": "pe_ratio", "title": "P/E Ratio",
        "summary": "How much you pay per rupee of company profit.",
        "detail": (
            "P/E = LTP ÷ EPS. Example: LTP Rs.1,200, EPS Rs.80 → P/E = 15. "
            "Low P/E vs sector avg: potentially undervalued. High P/E: growth expected or overvalued. "
            "Always compare P/E within the same sector."
        ),
        "tags": ["pe ratio", "p/e", "price to earnings", "eps", "valuation", "overvalued", "undervalued"],
    },
    {
        "id": "eps", "title": "EPS (Earnings Per Share)",
        "summary": "Company profit divided by total shares — higher is better.",
        "detail": (
            "EPS = Net Profit ÷ Total Shares. "
            "Example: Rs.8B profit, 100M shares → EPS = Rs.80. "
            "Growing EPS year-on-year signals a healthy, expanding company. "
            "Published in annual reports and aggregator sites like Merolagani."
        ),
        "tags": ["eps", "earnings per share", "profit", "valuation", "annual report"],
    },
]


def search(query: str, max_results: int = 3) -> list[dict]:
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
    return next((e for e in KNOWLEDGE_BASE if e.get("id") == entry_id), None)


def get_all_topics() -> list[dict]:
    return [{"id": e["id"], "title": e["title"], "summary": e["summary"]} for e in KNOWLEDGE_BASE]


def format_for_ai(entries: list[dict]) -> str:
    if not entries:
        return ""
    return "\n\n".join(
        f"## {e['title']}\n{e['summary']}\n{e['detail']}" for e in entries
    )


def get_context_for_query(query: str) -> str:
    return format_for_ai(search(query, max_results=2))