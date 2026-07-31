from __future__ import annotations

from typing import Generator

import pytest
from sqlalchemy import delete

from app.db.session import SessionLocal
from app.models.game_result import GameResult


@pytest.fixture(autouse=True)
def clean_game_results_table() -> Generator[None, None, None]:
    """Ensure the `game_results` table starts empty for every test."""
    session = SessionLocal()
    try:
        session.execute(delete(GameResult))
        session.commit()
        yield
    finally:
        session.close()
