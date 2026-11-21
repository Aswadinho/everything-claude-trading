import pandas as pd

from src.strategy import evaluate


def settings():
    return {
        "range_lookback": 20,
        "atr_period": 14,
        "relative_volume_min": 1.5,
        "close_location_long_min": 0.70,
        "close_location_short_max": 0.30,
        "retest_tolerance_atr": 0.25,
        "stop_buffer_atr": 0.20,
        "minimum_reward_risk": 2.0,
    }


def sample_frame():
    rows = []
    for i in range(35):
        rows.append({
            "timestamp": pd.Timestamp("2026-01-01", tz="UTC") + pd.Timedelta(hours=4*i),
            "open": 97.0, "high": 100.0, "low": 95.0,
            "close": 98.0, "volume": 100.0,
        })
    rows.append({
        "timestamp": pd.Timestamp("2026-01-06", tz="UTC"),
        "open": 100.0, "high": 104.0, "low": 99.5,
        "close": 103.5, "volume": 220.0,
    })
    rows.append({
        "timestamp": pd.Timestamp("2026-01-06 04:00", tz="UTC"),
        "open": 103.0, "high": 104.0, "low": 102.5,
        "close": 103.8, "volume": 130.0,
    })
    return pd.DataFrame(rows)


def test_confirms_long_breakout_retest():
    signal = evaluate(sample_frame(), settings())
    assert signal is not None
    assert signal["direction"] == "LONG"
    assert signal["stop"] < signal["entry"] < signal["target"]
    assert signal["risk_reward"] >= 2.0


def test_returns_none_when_volume_filter_fails():
    frame = sample_frame()
    frame.loc[35, "volume"] = 100.0
    assert evaluate(frame, settings()) is None


def test_returns_none_with_insufficient_history():
    assert evaluate(sample_frame().head(10), settings()) is None
