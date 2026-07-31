"""Pydantic schemas for game result creation and scoreboard summary."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class GameCreate(BaseModel):
    winner: str = Field(..., description="Winner of the game (e.g. 'X', 'O', or 'draw')")
    board_snapshot: str = Field(
        ..., description="Serialized board state at game completion (e.g. JSON string)"
    )
    completed_at: Optional[datetime] = Field(
        None, description="Timestamp when the game completed (server will default if unset)"
    )
    summary: Optional[str] = Field(
        None, description="Optional human-readable summary or notes about the game"
    )


class ScoreSummary(BaseModel):
    winner: str = Field(..., description="Player identifier")
    wins: int = Field(..., description="Total wins for the player")
