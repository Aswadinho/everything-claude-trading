from __future__ import annotations

import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]


def load_settings() -> dict:
    load_dotenv(ROOT / ".env")
    with (ROOT / "config" / "settings.yaml").open("r", encoding="utf-8") as handle:
        settings = yaml.safe_load(handle) or {}
    settings["telegram"] = {
        "bot_token": os.getenv("TELEGRAM_BOT_TOKEN", "").strip(),
        "chat_id": os.getenv("TELEGRAM_CHAT_ID", "").strip(),
    }
    settings["database_path"] = os.getenv(
        "SIGNALS_DB_PATH", str(ROOT / "data" / "signals.db")
    )
    return settings
