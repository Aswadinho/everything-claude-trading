from __future__ import annotations

import requests


def format_message(exchange_id: str, symbol: str, timeframe: str, signal: dict) -> str:
    return (
        f"ASWAD CRYPTO SIGNAL\\n"
        f"{exchange_id.upper()} | {symbol} | {timeframe}\\n"
        f"Setup: {signal['direction']} breakout + retest\\n"
        f"Entry reference: {signal['entry']:.8g}\\n"
        f"Invalidation / stop: {signal['stop']:.8g}\\n"
        f"Target reference: {signal['target']:.8g}\\n"
        f"R:R: {signal['risk_reward']:.2f}R\\n"
        f"Relative volume: {signal['relative_volume']:.2f}x\\n"
        f"Breakout level: {signal['breakout_level']:.8g}\\n"
        f"Closed candle: {signal['signal_time']}\\n"
        f"Manual execution only. Verify price, fees and liquidity before acting."
    )


def send_telegram(token: str, chat_id: str, message: str) -> None:
    if not token or not chat_id:
        print(message)
        return
    response = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": message},
        timeout=15,
    )
    response.raise_for_status()
