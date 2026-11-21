from src.storage import (
    close_signal, get_open_signals, initialise, performance_summary, save_once
)


def test_signal_is_deduplicated_and_outcome_is_tracked(tmp_path):
    database = str(tmp_path / "signals.db")
    initialise(database)
    signal = {
        "signal_time": "2026-02-01T00:00:00+00:00",
        "direction": "LONG", "entry": 100.0, "stop": 95.0,
        "target": 110.0, "relative_volume": 1.8,
    }
    assert save_once(database, "binance", "BTC/USDT", "4h", signal) is True
    assert save_once(database, "binance", "BTC/USDT", "4h", signal) is False
    open_signals = get_open_signals(database, "binance", "BTC/USDT", "4h")
    assert len(open_signals) == 1
    close_signal(database, open_signals[0]["id"], "WIN",
                 "2026-02-01T04:00:00+00:00", 110.0, 2.0)
    summary = performance_summary(database)
    assert summary["closed_signals"] == 1
    assert summary["win_rate_pct"] == 100.0
