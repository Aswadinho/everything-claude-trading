from __future__ import annotations

import argparse
import logging
import time

from src.config import load_settings
from src.market_data import fetch_candles, make_exchange
from src.monitor import update_outcomes
from src.notifier import format_message, send_telegram
from src.storage import initialise, performance_summary, save_once
from src.strategy import evaluate

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def scan_once(settings: dict) -> None:
    strategy_cfg = settings["strategy"]
    database_path = settings["database_path"]
    telegram = settings["telegram"]
    initialise(database_path)

    for exchange_id in settings["exchanges"]:
        try:
            exchange = make_exchange(exchange_id)
            exchange.load_markets()
        except Exception as exc:
            logging.warning("%s unavailable: %s", exchange_id, exc)
            continue

        for symbol in settings["symbols"]:
            for timeframe in settings["timeframes"]:
                try:
                    candles = fetch_candles(
                        exchange, symbol, timeframe, int(strategy_cfg["candle_limit"])
                    )
                    updated = update_outcomes(
                        database_path, exchange_id, symbol, timeframe, candles
                    )
                    if updated:
                        logging.info("Closed %d tracked signal(s): %s %s %s",
                                     updated, exchange_id, symbol, timeframe)
                    signal = evaluate(candles, strategy_cfg)
                    if signal and save_once(
                        database_path, exchange_id, symbol, timeframe, signal
                    ):
                        message = format_message(exchange_id, symbol, timeframe, signal)
                        send_telegram(telegram["bot_token"], telegram["chat_id"], message)
                        logging.info("New signal: %s %s %s", exchange_id, symbol, timeframe)
                except Exception as exc:
                    logging.warning("Skipped %s %s %s: %s",
                                     exchange_id, symbol, timeframe, exc)
                time.sleep(float(settings["scanner"]["rate_limit_seconds"]))


def main() -> None:
    parser = argparse.ArgumentParser(description="Aswad Crypto Signals scanner")
    parser.add_argument("--loop", action="store_true", help="Repeat scans continuously")
    parser.add_argument("--interval", type=int, default=300,
                        help="Seconds between full scans (default: 300)")
    parser.add_argument("--performance", action="store_true",
                        help="Print tracked signal performance and exit")
    args = parser.parse_args()
    settings = load_settings()
    initialise(settings["database_path"])
    if args.performance:
        import json
        print(json.dumps(performance_summary(settings["database_path"]), indent=2))
        return
    while True:
        scan_once(settings)
        if not args.loop:
            break
        logging.info("Scan complete. Sleeping %d seconds.", args.interval)
        time.sleep(max(30, args.interval))


if __name__ == "__main__":
    main()
