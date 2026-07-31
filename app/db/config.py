"""SQLite configuration for local development and local migration bootstrapping."""

from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_NAME = os.environ.get("GAME_RESULTS_DB_NAME", "game_results.db")
DB_PATH = DATA_DIR / DB_NAME

#: The connection string used throughout the application for development.
DATABASE_URL = os.environ.get("GAME_RESULTS_DATABASE_URL", f"sqlite:///{DB_PATH}")
