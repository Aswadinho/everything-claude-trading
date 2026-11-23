from __future__ import annotations

from src.storage import close_signal, get_open_signals


def update_outcomes(database_path: str, exchange_id: str, symbol: str,
                    timeframe: str, candles) -> int:
    """Close tracked signals when stop/target is touched by a later closed candle.

    If both are touched in the same candle, count the stop first. This is
    deliberately conservative because OHLCV does not reveal intrabar sequence.
    """
    updated = 0
    for signal in get_open_signals(database_path, exchange_id, symbol, timeframe):
        entry = float(signal["entry"])
        stop = float(signal["stop"])
        target = float(signal["target"])
        risk = entry - stop if signal["direction"] == "LONG" else stop - entry
        if risk <= 0:
            continue
        for _, candle in candles.iterrows():
            candle_time = candle["timestamp"].isoformat()
            if candle_time <= signal["signal_time"]:
                continue
            if signal["direction"] == "LONG":
                stop_hit = float(candle["low"]) <= stop
                target_hit = float(candle["high"]) >= target
                if stop_hit:
                    outcome, exit_price = "LOSS", stop
                elif target_hit:
                    outcome, exit_price = "WIN", target
                else:
                    continue
                realized_r = (exit_price - entry) / risk
            else:
                stop_hit = float(candle["high"]) >= stop
                target_hit = float(candle["low"]) <= target
                if stop_hit:
                    outcome, exit_price = "LOSS", stop
                elif target_hit:
                    outcome, exit_price = "WIN", target
                else:
                    continue
                realized_r = (entry - exit_price) / risk
            close_signal(database_path, int(signal["id"]), outcome,
                         candle_time, exit_price, realized_r)
            updated += 1
            break
    return updated
