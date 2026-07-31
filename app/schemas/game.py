"""Pydantic schemas for game result creation and scoreboard summary."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator

from ..models.game_result import GameMode as PersistedGameMode, Winner


class Mode(str, Enum):
    """Permitted game modes for starting a match."""

    SINGLE = "single"
    VERSUS = "versus"


class GameCreate(BaseModel):
    winner: Winner = Field(..., description="Winner of the game (either 'X', 'O', or 'draw')")
    board_snapshot: str = Field(
        ..., description="Serialized board state at game completion (e.g. JSON string)"
    )
    completed_at: Optional[datetime] = Field(
        None, description="Timestamp when the game completed (server will default if unset)"
    )
    summary: Optional[str] = Field(
        None, description="Optional human-readable summary or notes about the game"
    )
    mode: Mode = Field(
        Mode.SINGLE,
        description="Mode of the match ('single' for 1 vs Computer or 'versus' for local multiplayer)",
    )

    @validator("mode", pre=True)
    def normalize_mode_aliases(cls, value):
        if value is None:
            return Mode.SINGLE
        if isinstance(value, Mode):
            return value
        mode_value = str(value).strip().lower()
        if mode_value == "1 vs 1":
            return Mode.VERSUS
        try:
            return Mode(mode_value)
        except ValueError:
            raise ValueError(
                f"Unsupported mode '{value}'. Must be one of: {', '.join(sorted(item.value for item in Mode))}."
            )


class GameResultResponse(BaseModel):
    id: UUID = Field(..., description="Identifier of the persisted game result")
    recorded_at: datetime = Field(..., description="Timestamp when the result was stored")


class ScoreSummary(BaseModel):
    winner: str = Field(..., description="Player identifier")
    wins: int = Field(..., description="Total wins for the player")


class ScoreSummaryWithMode(ScoreSummary):
    mode: Mode = Field(..., description="Mode of the match that produced the returned summary")


class GamesSummary(BaseModel):
    player_wins: int = Field(..., description="Total number of games the human player (X) won")
    computer_wins: int = Field(..., description="Total number of games the computer (O) won")
    draws: int = Field(..., description="Total number of games that ended in a draw")


class ScoreboardSummary(BaseModel):
    x_wins: int = Field(..., description="Total number of wins for player X")
    o_wins: int = Field(..., description="Total number of wins for player O")
    draws: int = Field(..., description="Total number of games that ended in a draw")
