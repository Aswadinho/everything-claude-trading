import pandas as pd

from src.monitor import update_outcomes
from src.storage import get_open_signals, initialise, save_once, performance_summary


def test_monitor_uses_stop_first_when_both_levels_hit(tmp_path):
    database = str(tmp_path / "signals.db")
    initialise(database)
    signal = {
        "signal_time": "2026-01-01T00:00:00+00:00",
        "direction": "LONG", "entry": 100.0, "stop": 95.0,
        "target": 110.0, "relative_volume": 1.7,
    }
    save_once(database, "binance", "BTC/USDT", "4h", signal)
    candles = pd.DataFrame([{
        "timestamp": pd.Timestamp("2026-01-01T04:00:00Z"),
        "open": 100, "high": 111, "low": 94, "close": 105, "volume": 100,
    }])
    assert update_outcomes(database, "binance", "BTC/USDT", "4h", candles) == 1
    assert get_open_signals(database, "binance", "BTC/USDT", "4h") == []
    assert performance_summary(database)["total_r"] == -1.0
