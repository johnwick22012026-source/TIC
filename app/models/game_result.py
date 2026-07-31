"""ORM types for finished Tic-Tac-Toe games and their persisted outcomes."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime, String
from sqlalchemy.sql import func

from ..db.base import Base


class GameOutcome(str, Enum):
    IN_PROGRESS = "in_progress"
    X_WIN = "x_won"
    O_WIN = "o_won"
    DRAW = "draw"


class GameResults(Base):
    """Persistent record for a single finished game outcome."""

    __tablename__ = "game_results"

    id: str = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        unique=True,
        nullable=False,
    )
    winner: str = Column(
        String(32),
        nullable=False,
    )
    played_at: datetime = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


GameResult = GameResults
