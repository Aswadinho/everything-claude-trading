from __future__ import annotations

import ccxt
import pandas as pd


def make_exchange(exchange_id: str):
    exchange_class = getattr(ccxt, exchange_id, None)
    if exchange_class is None:
        raise ValueError(f"Unsupported CCXT exchange: {exchange_id}")
    return exchange_class({"enableRateLimit": True, "timeout": 20000})


def fetch_candles(exchange, symbol: str, timeframe: str, limit: int) -> pd.DataFrame:
    if not exchange.markets:
        exchange.load_markets()
    if symbol not in exchange.markets:
        raise ValueError(f"{symbol} is not listed on {exchange.id}")
    rows = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    if not rows or len(rows) < 30:
        raise ValueError("Insufficient OHLCV history")
    frame = pd.DataFrame(
        rows, columns=["timestamp", "open", "high", "low", "close", "volume"]
    )
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], unit="ms", utc=True)
    # The final OHLCV row is normally the still-forming candle. Never signal on it.
    return frame.iloc[:-1].reset_index(drop=True)
