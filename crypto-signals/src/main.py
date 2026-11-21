from __future__ import annotations

import logging
import time

from src.config import load_settings
from src.market_data import fetch_candles, make_exchange
from src.notifier import format_message, send_telegram
from src.storage import initialise, save_once
from src.strategy import evaluate

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def main() -> None:
    settings = load_settings()
    strategy_cfg = settings["strategy"]
    database_path = settings["database_path"]
    initialise(database_path)
    telegram = settings["telegram"]

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
                    signal = evaluate(candles, strategy_cfg)
                    if signal and save_once(
                        database_path, exchange_id, symbol, timeframe, signal
                    ):
                        message = format_message(exchange_id, symbol, timeframe, signal)
                        send_telegram(
                            telegram["bot_token"], telegram["chat_id"], message
                        )
                        logging.info("New signal: %s %s %s", exchange_id, symbol, timeframe)
                except Exception as exc:
                    logging.debug(
                        "Skipped %s %s %s: %s", exchange_id, symbol, timeframe, exc
                    )
                time.sleep(float(settings["scanner"]["rate_limit_seconds"]))


if __name__ == "__main__":
    main()
