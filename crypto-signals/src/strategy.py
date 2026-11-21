from __future__ import annotations

import pandas as pd


def _atr(frame: pd.DataFrame, period: int) -> pd.Series:
    previous_close = frame["close"].shift(1)
    true_range = pd.concat(
        [
            frame["high"] - frame["low"],
            (frame["high"] - previous_close).abs(),
            (frame["low"] - previous_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return true_range.rolling(period).mean()


def evaluate(frame: pd.DataFrame, cfg: dict) -> dict | None:
    """Return a confirmed breakout/retest signal, or None.

    The penultimate closed candle must break the preceding range. The latest
    closed candle must retest that level and close back in the breakout direction.
    """
    lookback = int(cfg["range_lookback"])
    atr_period = int(cfg["atr_period"])
    if len(frame) < max(lookback + 5, atr_period + 5):
        return None

    data = frame.copy()
    data["atr"] = _atr(data, atr_period)
    breakout = data.iloc[-2]
    confirm = data.iloc[-1]
    prior = data.iloc[-(lookback + 2):-2]
    atr = float(confirm["atr"])
    if pd.isna(atr) or atr <= 0:
        return None

    resistance = float(prior["high"].max())
    support = float(prior["low"].min())
    avg_volume = float(prior["volume"].mean())
    if avg_volume <= 0:
        return None

    volume_ratio = float(breakout["volume"]) / avg_volume
    if volume_ratio < float(cfg["relative_volume_min"]):
        return None

    candle_range = max(float(breakout["high"] - breakout["low"]), 1e-12)
    close_location = (float(breakout["close"]) - float(breakout["low"])) / candle_range
    tolerance = atr * float(cfg["retest_tolerance_atr"])
    stop_buffer = atr * float(cfg["stop_buffer_atr"])
    direction = None
    level = None

    if (
        float(breakout["close"]) > resistance
        and close_location >= float(cfg["close_location_long_min"])
        and float(confirm["low"]) <= resistance + tolerance
        and float(confirm["close"]) > resistance
        and float(confirm["close"]) > float(confirm["open"])
    ):
        direction, level = "LONG", resistance
        stop = min(float(confirm["low"]), level) - stop_buffer
        entry = float(confirm["close"])
        risk = entry - stop
        target = entry + risk * float(cfg["minimum_reward_risk"])
    elif (
        float(breakout["close"]) < support
        and close_location <= float(cfg["close_location_short_max"])
        and float(confirm["high"]) >= support - tolerance
        and float(confirm["close"]) < support
        and float(confirm["close"]) < float(confirm["open"])
    ):
        direction, level = "SHORT", support
        stop = max(float(confirm["high"]), level) + stop_buffer
        entry = float(confirm["close"])
        risk = stop - entry
        target = entry - risk * float(cfg["minimum_reward_risk"])
    else:
        return None

    if risk <= 0 or target <= 0:
        return None
    rr = abs(target - entry) / risk
    if rr < float(cfg["minimum_reward_risk"]):
        return None

    return {
        "direction": direction,
        "entry": entry,
        "stop": stop,
        "target": target,
        "risk_reward": rr,
        "breakout_level": float(level),
        "relative_volume": volume_ratio,
        "signal_time": confirm["timestamp"].isoformat(),
        "close": float(confirm["close"]),
    }
