# analysis.py
import os
import logging
import pandas as pd

logger = logging.getLogger(__name__)

DATA_FOLDER = "data"
SIDEWAYS_THRESHOLD_PCT = 1.5


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [col.strip().lower() for col in df.columns]
    if "ltp" in df.columns and "close" not in df.columns:
        df = df.rename(columns={"ltp": "close"})
    return df


def load_data(symbol: str) -> pd.DataFrame:
    symbol = symbol.upper().strip()
    preferred = os.path.join(DATA_FOLDER, f"{symbol}.csv")
    legacy    = os.path.join(DATA_FOLDER, f"{symbol}_2000-01-01_2021-12-31.csv")

    if os.path.exists(preferred):
        path = preferred
    elif os.path.exists(legacy):
        path = legacy
    else:
        raise FileNotFoundError(f"No data file found for '{symbol}'. Expected: {preferred}")

    df = _normalize_columns(pd.read_csv(path))

    if "close" not in df.columns:
        raise ValueError(f"No 'close' or 'ltp' column for {symbol}. Columns: {list(df.columns)}")

    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df = df.dropna(subset=["close"]).reset_index(drop=True)

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.sort_values("date").reset_index(drop=True)

    return df


def _sma(series: pd.Series, window: int) -> float | None:
    if len(series) < window:
        return None
    return round(float(series.iloc[-window:].mean()), 2)


def _rsi(series: pd.Series, period: int = 14) -> float | None:
    if len(series) < period + 1:
        return None
    delta    = series.diff().dropna()
    avg_gain = delta.clip(lower=0).iloc[-period:].mean()
    avg_loss = (-delta).clip(lower=0).iloc[-period:].mean()
    if avg_loss == 0:
        return 100.0
    return round(100 - (100 / (1 + avg_gain / avg_loss)), 2)


def _trend(series: pd.Series) -> str:
    sma20 = _sma(series, 20)
    sma50 = _sma(series, 50)

    if sma20 is not None and sma50 is not None:
        pct = ((sma20 - sma50) / sma50 * 100) if sma50 != 0 else 0
    elif len(series) >= 10:
        old = float(series.iloc[-10])
        pct = ((float(series.iloc[-1]) - old) / old * 100) if old != 0 else 0
    else:
        return "unknown"

    if pct > SIDEWAYS_THRESHOLD_PCT:   return "uptrend"
    if pct < -SIDEWAYS_THRESHOLD_PCT:  return "downtrend"
    return "sideways"


def _rsi_label(rsi: float | None) -> str:
    if rsi is None:      return "N/A"
    if rsi >= 70:        return f"{rsi} (Overbought — pullback possible)"
    if rsi <= 30:        return f"{rsi} (Oversold — bounce possible)"
    return f"{rsi} (Neutral)"


def get_market_data(symbol: str) -> dict:
    symbol = symbol.upper().strip()
    try:
        df = load_data(symbol)
    except FileNotFoundError as e:
        logger.warning(str(e))
        return {"error": str(e), "summary": f"No data for {symbol}.", "trend": "unknown"}
    except Exception as e:
        logger.error(f"Error loading {symbol}: {e}")
        return {"error": str(e), "summary": "Could not load market data.", "trend": "unknown"}

    close = df["close"]
    ltp        = round(float(close.iloc[-1]), 2)
    prev_close = round(float(close.iloc[-2]), 2) if len(close) >= 2 else ltp
    change_pct = round(((ltp - prev_close) / prev_close * 100), 2) if prev_close else 0.0
    sign       = "+" if change_pct >= 0 else ""

    latest_date = (
        str(df["date"].iloc[-1].date())
        if "date" in df.columns and pd.notna(df["date"].iloc[-1]) else "N/A"
    )

    window    = df.iloc[-252:] if len(df) >= 252 else df
    week_high = round(float(window["close"].max()), 2)
    week_low  = round(float(window["close"].min()), 2)

    volume = None
    for col in ["volume", "vol", "quantity", "traded quantity"]:
        if col in df.columns:
            raw = pd.to_numeric(df[col].iloc[-1], errors="coerce")
            if pd.notna(raw):
                volume = int(raw)
            break

    rsi_val = _rsi(close)
    sma20   = _sma(close, 20)
    sma50   = _sma(close, 50)
    trend   = _trend(close)

    summary = (
        f"{symbol} last traded at Rs. {ltp:,} on {latest_date} "
        f"({sign}{change_pct}% change). Trend: {trend}. "
        f"RSI: {_rsi_label(rsi_val)}. "
        f"52-week range: Rs. {week_low:,} – Rs. {week_high:,}."
    )

    return {
        "ltp":     ltp,
        "change":  f"{sign}{change_pct}%",
        "high":    f"Rs. {week_high:,} (52-week high)",
        "low":     f"Rs. {week_low:,} (52-week low)",
        "volume":  f"{volume:,} kitta" if volume is not None else "N/A",
        "trend":   trend,
        "rsi":     _rsi_label(rsi_val),
        "sma20":   f"Rs. {sma20:,}" if sma20 else "N/A",
        "sma50":   f"Rs. {sma50:,}" if sma50 else "N/A",
        "date":    latest_date,
        "summary": summary,
    }