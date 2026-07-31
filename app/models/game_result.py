"""ORM model representing a single finished Tic-Tac-Toe game result."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Column, DateTime, Enum as SQLAEnum, String, Text
from sqlalchemy.sql import func

from ..db.base import Base


class GameOutcome(str, Enum):
    IN_PROGRESS = "in_progress"
    X_WIN = "x_win"
    O_WIN = "o_win"
    DRAW = "draw"


class GameResult(Base):
    """A finished game persisted for historical scoreboards."""

    __tablename__ = "game_results"

    id: str = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        unique=True,
        nullable=False,
    )
    outcome_id: str = Column(
        String(36),
        unique=True,
        nullable=False,
        default=lambda: str(uuid.uuid4()),
    )
    created_at: datetime = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    completed_at: Optional[datetime] = Column(
        DateTime(timezone=True),
        nullable=True,
    )
    recorded_at: datetime = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    status: GameOutcome = Column(
        SQLAEnum(GameOutcome, name="game_outcome_status", native_enum=False),
        nullable=False,
        default=GameOutcome.IN_PROGRESS,
    )
    winner: Optional[str] = Column(
        String(32),
        nullable=True,
    )
    board_snapshot: str = Column(
        Text,
        nullable=False,
    )
    summary: Optional[str] = Column(
        Text,
        nullable=True,
    )
