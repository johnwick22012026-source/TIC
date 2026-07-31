"""ORM model representing a single finished Tic-Tac-Toe game result."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.sql import func

from ..db.base import Base


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
    created_at: datetime = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    completed_at: Optional[datetime] = Column(
        DateTime(timezone=True),
        nullable=True,
    )
    winner: str = Column(
        String(32),
        nullable=False,
    )
    board_snapshot: str = Column(
        Text,
        nullable=False,
    )
    summary: Optional[str] = Column(
        Text,
        nullable=True,
    )
