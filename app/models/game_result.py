"""ORM types for finished Tic-Tac-Toe games and their persisted outcomes."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Column, DateTime, Enum as SQLEnum, String, Text
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
        index=True,
    )
    status: GameOutcome = Column(
        SQLEnum(GameOutcome, name="game_outcome", native_enum=False),
        nullable=False,
        default=GameOutcome.IN_PROGRESS,
        server_default=GameOutcome.IN_PROGRESS.value,
    )
    board_snapshot: str = Column(
        Text,
        nullable=False,
    )
    summary: Optional[str] = Column(
        Text,
        nullable=True,
    )
    completed_at: datetime = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    recorded_at: datetime = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


GameResult = GameResults
