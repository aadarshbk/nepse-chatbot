# nepse_data.py
"""
NEPSE Data Fetcher — currently uses safe stubs (no random fake data).
Replace each STUB block with a real scraper when ready.
Good sources: nepalstock.com.np | merolagani.com | nepsealpha.com
"""
import datetime
import logging
import time

logger = logging.getLogger(__name__)

NST_OFFSET    = datetime.timezone(datetime.timedelta(hours=5, minutes=45))
TRADING_DAYS  = {6, 0, 1, 2, 3}   # Sun=6, Mon=0, Tue=1, Wed=2, Thu=3
MARKET_OPEN   = datetime.time(11, 0)
MARKET_CLOSE  = datetime.time(15, 0)
CACHE_TTL_SEC = 60


def _now_nst() -> datetime.datetime:
    return datetime.datetime.now(tz=NST_OFFSET)


class NepseDataFetcher:
    def __init__(self):
        self._cache: dict[str, tuple] = {}

    def _get_cached(self, key: str):
        entry = self._cache.get(key)
        if not entry:
            return None
        value, ts = entry
        if time.monotonic() - ts > CACHE_TTL_SEC:
            del self._cache[key]
            return None
        return value

    def _set_cache(self, key: str, value) -> None:
        self._cache[key] = (value, time.monotonic())

    def get_market_status(self) -> str:
        cached = self._get_cached("market_status")
        if cached:
            return cached
        now     = _now_nst()
        weekday = now.weekday()
        current = now.time().replace(second=0, microsecond=0)
        if weekday not in TRADING_DAYS:
            status = "Closed (weekend)"
        elif MARKET_OPEN <= current < MARKET_CLOSE:
            status = "Open"
        else:
            status = "Closed (outside trading hours)"
        self._set_cache("market_status", status)
        return status

    def get_market_summary(self) -> dict:
        cached = self._get_cached("market_summary")
        if cached:
            return cached
        # ── STUB ──────────────────────────────────────────────────────────────
        summary = {
            "close": "N/A", "date": _now_nst().strftime("%Y-%m-%d"),
            "volume": "N/A", "transactions": "N/A",
            "note": "Live data not yet connected.",
        }
        # ── END STUB ──────────────────────────────────────────────────────────
        self._set_cache("market_summary", summary)
        return summary

    def get_market_trend(self) -> str:
        cached = self._get_cached("market_trend")
        if cached:
            return cached
        # ── STUB ──────────────────────────────────────────────────────────────
        trend = "neutral"
        # ── END STUB ──────────────────────────────────────────────────────────
        self._set_cache("market_trend", trend)
        return trend

    def get_nepse_index(self) -> dict:
        cached = self._get_cached("nepse_index")
        if cached:
            return cached
        now = _now_nst()
        # ── STUB ──────────────────────────────────────────────────────────────
        index_data = {
            "index_name": "NEPSE", "value": "N/A", "change": "N/A",
            "date": now.strftime("%Y-%m-%d"), "time": now.strftime("%H:%M NST"),
            "note": "Live data not yet connected.",
        }
        # ── END STUB ──────────────────────────────────────────────────────────
        self._set_cache("nepse_index", index_data)
        return index_data

    def get_live_price(self, symbol: str) -> dict:
        symbol    = symbol.upper().strip()
        cache_key = f"stock_{symbol}"
        cached    = self._get_cached(cache_key)
        if cached:
            return cached
        # ── STUB ──────────────────────────────────────────────────────────────
        price_data = {
            "symbol": symbol, "ltp": "N/A", "change": "N/A",
            "percent_change": "N/A", "market_status": self.get_market_status(),
            "timestamp": _now_nst().isoformat(),
            "note": "Live price data not yet connected.",
        }
        # ── END STUB ──────────────────────────────────────────────────────────
        self._set_cache(cache_key, price_data)
        return price_data

    def clear_cache(self) -> None:
        self._cache.clear()


nepse_fetcher = NepseDataFetcher()