# Aswad Crypto Signals

A manual-execution crypto market scanner built alongside the Everything Claude Trading Claude Code toolkit.

## What it does

- Scans configured spot markets across multiple exchanges through public market-data endpoints.
- Starts with BTC, ETH, SOL, HYPE and LINK against USDT on Binance, Bybit, OKX and MEXC (only where a symbol is listed).
- Analyses 4h and 1d candles.
- Looks for a range breakout followed by a successful retest, with relative-volume and candle-close-location filters.
- Calculates an invalidation level and a 2R reference target.
- Sends Telegram alerts and stores signals in SQLite to prevent repeated alerts.

**Alerts only.** This project does not place orders, connect trading accounts, request exchange API keys, or manage positions.

## Strategy status

The rule set is an experimental hypothesis, not a demonstrated profitable strategy. Thresholds are configurable and must be tested with historical data, realistic fees/slippage, out-of-sample periods and paper observation before being considered useful. Signals are not financial advice.

## Setup

Requires Python 3.11+.

```bash
cd crypto-signals
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env`, then add your Telegram bot token and chat ID if you want notifications. Never commit `.env`.

Run a scan:

```bash
python -m src.main
```

The scanner can run without Telegram credentials; it will print signals to the terminal.

## Initial configuration

Edit `config/settings.yaml` to change exchanges, symbols, timeframes, lookback, volume threshold, breakout/retest tolerance and minimum reward-to-risk ratio.

## Signal lifecycle

1. Fetch OHLCV candles from each exchange's public market-data API.
2. Ignore the currently-forming candle.
3. Find a prior range breakout.
4. Check whether the latest closed candle retested and held the breakout level.
5. Apply relative-volume and candle-close-location filters.
6. Calculate stop/invalidation and target reference.
7. Persist and notify once per exchange/symbol/timeframe/candle.

## Important limitations

- Exchange symbol availability and market conventions differ; unsupported pairs are skipped.
- Public endpoints can rate-limit or temporarily fail.
- A 4h or 1d candle is only confirmed after it closes.
- A 2R target is a planning reference, not a forecast.
- No position sizing or execution is performed by this application.
