import pandas as pd

from src.backtest import run_backtest


def test_backtest_returns_empty_report_for_no_setups():
    frame = pd.DataFrame([{
        "timestamp": pd.Timestamp("2026-01-01", tz="UTC") + pd.Timedelta(hours=4*i),
        "open": 100, "high": 101, "low": 99, "close": 100, "volume": 100,
    } for i in range(60)])
    cfg = {
        "range_lookback": 20, "atr_period": 14, "relative_volume_min": 1.5,
        "close_location_long_min": .7, "close_location_short_max": .3,
        "retest_tolerance_atr": .25, "stop_buffer_atr": .2, "minimum_reward_risk": 2,
    }
    report = run_backtest(frame, cfg)
    assert report["trade_count"] == 0
