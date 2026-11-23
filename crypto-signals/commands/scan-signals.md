# /scan-signals

Scan configured crypto spot markets for confirmed breakout-and-retest setups.

1. Read `crypto-signals/config/settings.yaml`.
2. Check the Python scanner implementation and explain its current signal conditions.
3. Run `python -m src.main` from the `crypto-signals` directory only if dependencies are installed and the user requests a live scan.
4. Never submit orders or request exchange trading credentials.
5. Report the exchange, pair, timeframe, direction, closed-candle timestamp, entry reference, invalidation, target reference, relative volume and R:R for every signal.
6. Clearly state when there are no qualifying signals; do not manufacture a setup.
7. Mention data/API failures separately from a genuine no-signal result.
