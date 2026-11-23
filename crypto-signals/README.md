# Aswad Crypto Signals

A multi-exchange crypto market scanner and research tool. It uses public market data and produces alerts for manual review; it never places orders.

## Initial universe

- Exchanges: Binance, Bybit, OKX and MEXC (a pair is skipped if not listed).
- Markets: BTC/USDT, ETH/USDT, SOL/USDT, HYPE/USDT and LINK/USDT.
- Timeframes: 4h and 1d.
- Setup: range breakout followed by a confirmed retest, relative-volume filter and candle-close-location filter.
- Alerts: terminal output or optional Telegram.
- Storage: SQLite signal history, duplicate suppression and stop/target outcome tracking.

## Safety and strategy status

This is an experimental rule-based strategy, not a proven profitable system or financial advice. Do not rely on live alerts until historical tests, out-of-sample validation and paper monitoring show acceptable results. There is no order execution, trading-account authentication, wallet access or exchange secret requirement.

The scanner ignores the currently forming candle. Signal entry references are calculated at confirmation close. The backtester assumes entry at the next candle open. For OHLCV candles where stop and target are both touched, it assumes the stop happened first.

## Install

Python 3.11+ is recommended.

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# macOS/Linux
# source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env`. Telegram credentials are optional. Never commit `.env`.

## Run a scan

From this directory:

```bash
python -m src.main
```

Run continuously (full scan every 5 minutes):

```bash
python -m src.main --loop --interval 300
```

View tracked signal outcomes:

```bash
python -m src.main --performance
```

The outcome tracker marks a signal WIN when its target is touched or LOSS when its stop is touched. If both are touched in one candle, it records LOSS conservatively. Outcomes are gross R multiples and do not include fees/slippage.

## Backtesting

Prepare a CSV with these columns: `timestamp,open,high,low,close,volume`. Use chronological OHLCV data for one exchange, symbol and timeframe. Do not mix symbols or timeframes.

```bash
python -m src.backtest path/to/ohlcv.csv --fee-bps 8 --slippage-bps 5
```

The backtester evaluates each candle using only data available through that candle close, enters at the next candle open, and exits at stop/target. It reports trade count, win rate, net R, average R, profit factor and max drawdown. If both stop and target are hit within a candle, stop is assumed first. Fees and slippage are approximate configurable basis-point assumptions, not exchange-specific fee accounting.

For a credible evaluation, use several market regimes, retain a separate untouched out-of-sample period, and compare against simple buy-and-hold / benchmark results. Review the full trade log, not only aggregate metrics.

## Claude Code

- `CLAUDE.md`: project safety rules and development standards.
- `commands/scan-signals.md`: instructions for reviewing/running a scan.
- `commands/review-strategy.md`: quantitative strategy review checklist.

## Known limitations

- Exchange OHLCV histories and symbol availability vary.
- Public endpoints may rate-limit or fail; failed markets are logged and skipped.
- Backtests use candle OHLCV and cannot reconstruct intrabar order or realistic liquidity.
- The backtester currently consumes a local CSV; it does not automatically download historical data.
- Live signal outcome tracking starts when this version is running and cannot reconstruct missed historical alerts.
- No portfolio-level exposure, position sizing or automated execution is implemented.
