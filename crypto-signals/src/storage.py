from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


def _connect(database_path: str) -> sqlite3.Connection:
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


def initialise(database_path: str) -> None:
    """Create the signal table and apply additive migrations safely."""
    with _connect(database_path) as connection:
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
                outcome TEXT,
                exit_time TEXT,
                exit_price REAL,
                realized_r REAL,
                UNIQUE(exchange, symbol, timeframe, signal_time, direction)
            )
            """
        )
        existing = {
            row["name"] for row in connection.execute("PRAGMA table_info(signals)")
        }
        migrations = {
            "outcome": "TEXT",
            "exit_time": "TEXT",
            "exit_price": "REAL",
            "realized_r": "REAL",
        }
        for column, sql_type in migrations.items():
            if column not in existing:
                connection.execute(f"ALTER TABLE signals ADD COLUMN {column} {sql_type}")


def save_once(database_path: str, exchange: str, symbol: str,
              timeframe: str, signal: dict) -> bool:
    with _connect(database_path) as connection:
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


def get_open_signals(database_path: str, exchange: str,
                     symbol: str, timeframe: str) -> list[dict[str, Any]]:
    with _connect(database_path) as connection:
        rows = connection.execute(
            """
            SELECT * FROM signals
            WHERE exchange = ? AND symbol = ? AND timeframe = ?
              AND outcome IS NULL
            ORDER BY signal_time ASC
            """,
            (exchange, symbol, timeframe),
        ).fetchall()
        return [dict(row) for row in rows]


def close_signal(database_path: str, signal_id: int, outcome: str,
                 exit_time: str, exit_price: float, realized_r: float) -> bool:
    if outcome not in {"WIN", "LOSS", "BREAKEVEN"}:
        raise ValueError("outcome must be WIN, LOSS, or BREAKEVEN")
    with _connect(database_path) as connection:
        cursor = connection.execute(
            """
            UPDATE signals
            SET outcome = ?, exit_time = ?, exit_price = ?, realized_r = ?
            WHERE id = ? AND outcome IS NULL
            """,
            (outcome, exit_time, exit_price, realized_r, signal_id),
        )
        return cursor.rowcount == 1


def performance_summary(database_path: str) -> dict[str, Any]:
    with _connect(database_path) as connection:
        row = connection.execute(
            """
            SELECT
                COUNT(*) AS total_signals,
                SUM(CASE WHEN outcome IS NOT NULL THEN 1 ELSE 0 END) AS closed_signals,
                SUM(CASE WHEN outcome IS NULL THEN 1 ELSE 0 END) AS open_signals,
                SUM(CASE WHEN outcome = 'WIN' THEN 1 ELSE 0 END) AS wins,
                SUM(CASE WHEN outcome = 'LOSS' THEN 1 ELSE 0 END) AS losses,
                SUM(CASE WHEN outcome = 'BREAKEVEN' THEN 1 ELSE 0 END) AS breakevens,
                COALESCE(SUM(realized_r), 0.0) AS total_realized_r
            FROM signals
            """
        ).fetchone()
    closed = int(row["closed_signals"] or 0)
    wins = int(row["wins"] or 0)
    return {
        "total_signals": int(row["total_signals"] or 0),
        "closed_signals": closed,
        "open_signals": int(row["open_signals"] or 0),
        "wins": wins,
        "losses": int(row["losses"] or 0),
        "breakevens": int(row["breakevens"] or 0),
        "win_rate_pct": round((wins / closed) * 100, 2) if closed else 0.0,
        "total_realized_r": round(float(row["total_realized_r"] or 0.0), 4),
    }
