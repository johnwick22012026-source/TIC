"""ORM types for finished Tic-Tac-Toe games and their persisted outcomes."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Column, DateTime, Enum as SQLEnum, Index, String, Text, func

from ..db.base import Base


class Winner(str, Enum):
    """Permitted winner values for a finished Tic-Tac-Toe game."""

    X = "X"
    O = "O"
    DRAW = "draw"


class GameOutcome(str, Enum):
    """Status values used to describe the terminal state of a recorded match."""

    IN_PROGRESS = "in_progress"
    X_WIN = "x_won"
    O_WIN = "o_won"
    DRAW = "draw"


class GameMode(str, Enum):
    """Configured match modes that can be persisted with a result."""

    SINGLE = "single"
    VERSUS = "versus"


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
    winner: Winner = Column(
        SQLEnum(Winner, name="game_winner", native_enum=False),
        nullable=False,
        index=True,
    )
    status: GameOutcome = Column(
        SQLEnum(GameOutcome, name="game_outcome", native_enum=False),
        nullable=False,
        default=GameOutcome.IN_PROGRESS,
        server_default=GameOutcome.IN_PROGRESS.value,
        index=True,
    )
    mode: GameMode = Column(
        SQLEnum(GameMode, name="game_mode", native_enum=False),
        nullable=False,
        default=GameMode.SINGLE,
        server_default=GameMode.SINGLE.value,
        index=True,
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
        default=func.now(),
        server_default=func.now(),
    )
    recorded_at: datetime = Column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        server_default=func.now(),
    )

    __table_args__ = (
        Index("idx_game_results_status", "status"),
        Index("idx_game_results_winner", "winner"),
        Index("idx_game_results_completed_at", "completed_at"),
        Index("idx_game_results_recorded_at", "recorded_at"),
        Index("idx_game_results_mode", "mode"),
    )

    def __repr__(self) -> str:  # pragma: no cover - representation helper
        return (
            f"<GameResults id={self.id} winner={self.winner} status={self.status} "
            f"mode={self.mode} completed_at={self.completed_at}>"
        )


GameResult = GameResults
