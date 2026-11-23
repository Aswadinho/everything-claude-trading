# Claude Code instructions — Aswad Crypto Signals

This repository contains the upstream Everything Claude Trading toolkit plus a separate Python alert-only scanner under `crypto-signals/`.

## Non-negotiable constraints

- This project is for market analysis and alerts only. Never add exchange order placement, trading-account authentication, withdrawals, transfers, or automatic execution.
- Use public market data only. Do not request or store exchange API secrets.
- Never claim a strategy is profitable without reproducible, out-of-sample evidence.
- Keep signals explainable: include exchange, symbol, timeframe, closed-candle timestamp, setup, entry reference, invalidation, target reference, relative volume and risk/reward.
- Never use the still-forming candle to generate a signal.
- Handle missing listings, API errors and rate limits without crashing the entire scan.
- Avoid duplicate alerts for the same exchange, symbol, timeframe, candle and direction.
- Keep secrets in `.env`; never commit credentials or personal chat identifiers.

## Current strategy hypothesis

The first implementation is a support/resistance breakout followed by a successful retest. It filters on relative volume, breakout candle close location and a minimum 2R target reference. These are configurable heuristics, not validated trading edge.

## Development priorities

1. Unit tests for long/short setups, false breakouts, insufficient history and candle closure.
2. Historical backtesting with fees, slippage, out-of-sample periods and no look-ahead bias.
3. Signal outcome tracking and paper monitoring.
4. More robust exchange symbol mapping and rate-limit/backoff handling.
5. Telegram formatting and operational logging.

Prefer small, testable Python functions. Preserve the upstream toolkit unless a change is specifically required for this scanner.
