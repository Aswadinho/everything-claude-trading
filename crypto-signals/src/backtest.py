from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from src.strategy import evaluate


def run_backtest(frame: pd.DataFrame, cfg: dict, fee_bps: float = 8.0,
                 slippage_bps: float = 5.0) -> dict:
    """Walk-forward test. Signal forms at candle close; entry is next candle open.

    If stop and target are both touched in one candle, stop is assumed first.
    Fees and slippage are charged on entry and exit notional as a conservative
    approximation. No look-ahead data is passed to the signal function.
    """
    data = frame.copy().reset_index(drop=True)
    required = {"timestamp", "open", "high", "low", "close", "volume"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"CSV is missing columns: {', '.join(sorted(missing))}")
    for col in ["open", "high", "low", "close", "volume"]:
        data[col] = pd.to_numeric(data[col], errors="coerce")
    data = data.dropna(subset=["open", "high", "low", "close", "volume"])
    trades = []
    warmup = max(int(cfg["range_lookback"]) + 5, int(cfg["atr_period"]) + 5)
    costs = 2 * (fee_bps + slippage_bps) / 10000

    for signal_idx in range(warmup, len(data) - 1):
        signal = evaluate(data.iloc[:signal_idx + 1], cfg)
        if not signal:
            continue
        entry_idx = signal_idx + 1
        entry = float(data.iloc[entry_idx]["open"])
        direction = signal["direction"]
        stop, target = float(signal["stop"]), float(signal["target"])
        risk = entry - stop if direction == "LONG" else stop - entry
        if risk <= 0:
            continue

        outcome, exit_price, exit_time = "OPEN", float(data.iloc[-1]["close"]), data.iloc[-1]["timestamp"]
        for j in range(entry_idx, len(data)):
            candle = data.iloc[j]
            if direction == "LONG":
                stop_hit = float(candle["low"]) <= stop
                target_hit = float(candle["high"]) >= target
            else:
                stop_hit = float(candle["high"]) >= stop
                target_hit = float(candle["low"]) <= target
            if stop_hit:  # conservative when both levels are touched in one candle
                outcome, exit_price, exit_time = "LOSS", stop, candle["timestamp"]
                break
            if target_hit:
                outcome, exit_price, exit_time = "WIN", target, candle["timestamp"]
                break

        gross_r = ((exit_price - entry) / risk if direction == "LONG"
                   else (entry - exit_price) / risk)
        cost_r = (entry * costs) / risk
        net_r = gross_r - cost_r
        trades.append({
            "signal_time": str(signal["signal_time"]),
            "entry_time": str(data.iloc[entry_idx]["timestamp"]),
            "direction": direction, "entry": entry, "stop": stop,
            "target": target, "exit": exit_price, "exit_time": str(exit_time),
            "outcome": outcome, "gross_r": gross_r, "net_r": net_r,
        })

    if not trades:
        return {"trade_count": 0, "trades": [], "message": "No qualifying setups in this dataset."}

    results = pd.DataFrame(trades)
    wins = results[results["net_r"] > 0]
    losses = results[results["net_r"] <= 0]
    gross_profit = float(wins["net_r"].sum())
    gross_loss = abs(float(losses["net_r"].sum()))
    equity = results["net_r"].cumsum()
    peak = equity.cummax()
    drawdown = equity - peak
    return {
        "trade_count": int(len(results)),
        "win_rate_pct": round(float((results["net_r"] > 0).mean() * 100), 2),
        "total_net_r": round(float(results["net_r"].sum()), 3),
        "average_net_r": round(float(results["net_r"].mean()), 3),
        "profit_factor": round(gross_profit / gross_loss, 3) if gross_loss else None,
        "max_drawdown_r": round(float(drawdown.min()), 3),
        "wins": int((results["net_r"] > 0).sum()),
        "losses": int((results["net_r"] <= 0).sum()),
        "open_at_end": int((results["outcome"] == "OPEN").sum()),
        "trades": trades,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Backtest Aswad Crypto Signals on OHLCV CSV.")
    parser.add_argument("csv", help="CSV with timestamp,open,high,low,close,volume")
    parser.add_argument("--fee-bps", type=float, default=8.0)
    parser.add_argument("--slippage-bps", type=float, default=5.0)
    parser.add_argument("--output", default="backtest-results.json")
    args = parser.parse_args()

    from src.config import load_settings
    settings = load_settings()
    frame = pd.read_csv(Path(args.csv))
    report = run_backtest(frame, settings["strategy"], args.fee_bps, args.slippage_bps)
    Path(args.output).write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "trades"}, indent=2))
    print(f"Full trade log: {args.output}")


if __name__ == "__main__":
    main()
