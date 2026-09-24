"""
Central configuration for the Experience-Aware Tool Memory Dashboard.

Loads environment variables and exposes a single Config object used
throughout the app. Nothing here requires an API key to function --
DEMO MODE is fully self-contained.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Load .env if present. If it isn't, the app still works in demo mode.
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Config:
    execution_mode: str
    anthropic_api_key: str | None
    openweather_api_key: str | None
    exchangerate_api_key: str | None
    sqlite_db_path: Path
    chroma_persist_dir: Path

    @property
    def is_live(self) -> bool:
        return self.execution_mode.lower() == "live"


def load_config() -> Config:
    mode = os.getenv("EXECUTION_MODE", "demo").strip().lower()
    if mode not in ("demo", "live"):
        mode = "demo"

    db_path = os.getenv("SQLITE_DB_PATH", "data/experiences.db")
    chroma_dir = os.getenv("CHROMA_PERSIST_DIR", "data/chroma_store")

    return Config(
        execution_mode=mode,
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY") or None,
        openweather_api_key=os.getenv("OPENWEATHER_API_KEY") or None,
        exchangerate_api_key=os.getenv("EXCHANGERATE_API_KEY") or None,
        sqlite_db_path=(BASE_DIR / db_path).resolve(),
        chroma_persist_dir=(BASE_DIR / chroma_dir).resolve(),
    )


CONFIG = load_config()
