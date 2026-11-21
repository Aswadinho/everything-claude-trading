from __future__ import annotations

import sqlite3
from pathlib import Path


def initialise(database_path: str) -> None:
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exchange TEXT NOT NULL,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                signal_time TEXT NOT NULL,
                direction TEXT NOT NULL,
                entry REAL NOT NULL,
                stop REAL NOT NULL,
                target REAL NOT NULL,
                relative_volume REAL NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(exchange, symbol, timeframe, signal_time, direction)
            )
            """
        )


def save_once(database_path: str, exchange: str, symbol: str,
              timeframe: str, signal: dict) -> bool:
    with sqlite3.connect(database_path) as connection:
        cursor = connection.execute(
            """
            INSERT OR IGNORE INTO signals
            (exchange, symbol, timeframe, signal_time, direction,
             entry, stop, target, relative_volume)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                exchange, symbol, timeframe, signal["signal_time"],
                signal["direction"], signal["entry"], signal["stop"],
                signal["target"], signal["relative_volume"],
            ),
        )
        return cursor.rowcount == 1
