# nepse_data.py
"""
NEPSE Data Fetcher
Handles market summary, index, status, and stock prices.
Currently uses mock data (safe stubs).
Can be replaced with real scraping/API logic later.
"""

import datetime
import random
import time


class NepseDataFetcher:
    def __init__(self):
        # Simple in-memory cache
        self.cache = {}
        self.cache_ttl = 60  # seconds

    # -------------------------------------------------------------------------
    # Utility: caching
    # -------------------------------------------------------------------------
    def _get_cached(self, key):
        data = self.cache.get(key)
        if not data:
            return None

        value, timestamp = data
        if time.time() - timestamp > self.cache_ttl:
            return None

        return value

    def _set_cache(self, key, value):
        self.cache[key] = (value, time.time())

    # -------------------------------------------------------------------------
    # Market Summary (Sidebar)
    # -------------------------------------------------------------------------
    def get_market_summary(self):
        """Returns data for the sidebar (close, date, volume, transactions)"""

        cached = self._get_cached("market_summary")
        if cached:
            return cached

        summary = {
            "close": round(random.uniform(2100, 2300), 2),
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "volume": f"{round(random.uniform(10, 25), 1)}M",
            "transactions": str(random.randint(400, 700))
        }

        self._set_cache("market_summary", summary)
        return summary

    # -------------------------------------------------------------------------
    # Market Trend
    # -------------------------------------------------------------------------
    def get_market_trend(self):
        """Returns overall market trend"""

        cached = self._get_cached("market_trend")
        if cached:
            return cached

        trend = random.choice([
            "Positive 🟢",
            "Negative 🔴",
            "Neutral ⚪"
        ])

        self._set_cache("market_trend", trend)
        return trend

    # -------------------------------------------------------------------------
    # NEPSE Index
    # -------------------------------------------------------------------------
    def get_nepse_index(self):
        """Returns NEPSE index data"""

        cached = self._get_cached("nepse_index")
        if cached:
            return cached

        index_data = {
            "index_name": "NEPSE",
            "value": round(random.uniform(2100, 2300), 2),
            "change": round(random.uniform(-25, 25), 2),
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.datetime.now().strftime("%H:%M:%S")
        }

        self._set_cache("nepse_index", index_data)
        return index_data

    # -------------------------------------------------------------------------
    # Market Status
    # -------------------------------------------------------------------------
    def get_market_status(self):
        """Returns whether market is open or closed"""

        now = datetime.datetime.now()
        hour = now.hour
        weekday = now.weekday()  # 0 = Monday, 6 = Sunday

        # NEPSE is typically closed on weekends
        if weekday >= 5:
            return "Market is CLOSED 🔴 (Weekend)"

        # Approx NEPSE trading hours (11:00 – 15:00)
        if 11 <= hour < 15:
            return "Market is OPEN 🟢"
        else:
            return "Market is CLOSED 🔴"

    # -------------------------------------------------------------------------
    # Live Stock Price
    # -------------------------------------------------------------------------
    def get_live_price(self, symbol):
        """Returns live price for a specific stock symbol"""

        symbol = symbol.upper()
        cache_key = f"stock_{symbol}"

        cached = self._get_cached(cache_key)
        if cached:
            return cached

        price_data = {
            "symbol": symbol,
            "ltp": round(random.uniform(300, 3000), 2),
            "change": round(random.uniform(-5, 5), 2),
            "percent_change": round(random.uniform(-3, 3), 2),
            "status": "Open" if "OPEN" in self.get_market_status() else "Closed",
            "timestamp": datetime.datetime.now().isoformat()
        }

        self._set_cache(cache_key, price_data)
        return price_data


# -------------------------------------------------------------------------
# Global instance (used by app.py)
# -------------------------------------------------------------------------
nepse_fetcher = NepseDataFetcher()