import pandas as pd
import os


DATA_FOLDER = "data"


def load_data(symbol: str):
    file_path = os.path.join(
        DATA_FOLDER,
        f"{symbol}_2000-01-01_2021-12-31.csv"
    )

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No data found for {symbol}")

    df = pd.read_csv(file_path)
    return df


def get_summary(symbol: str):
    df = load_data(symbol)

    if "close" not in df.columns:
        raise ValueError(f"'close' column not found. Available columns: {df.columns}")

    latest = df.iloc[-1]

    return {
        "close": float(latest["close"]),
        "date": latest["date"] if "date" in df.columns else "N/A"
    }


def get_trend(symbol: str):
    df = load_data(symbol)

    if len(df) < 10:
        return "unknown"

    if "close" not in df.columns:
        raise ValueError(f"'close' column not found. Available columns: {df.columns}")

    if df["close"].iloc[-1] > df["close"].iloc[-10]:
        return "uptrend"
    else:
        return "downtrend"


def get_market_data(symbol: str):
    return {
        "summary": get_summary(symbol),
        "trend": get_trend(symbol)
    }
