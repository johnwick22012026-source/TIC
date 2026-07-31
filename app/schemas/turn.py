"""Pydantic schemas for turn resolution (player X move then random O move)."""
from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field

from ..models.game_result import GameOutcome, GameMode
from ..schemas.game import ScoreboardSummary


class TurnRequest(BaseModel):
    board: List[str] = Field(
        ...,
        min_length=9,
        max_length=9,
        description="List of 9 cell values ('', 'X', or 'O') before the X move."
    )
    x_move: int = Field(..., ge=0, lt=9, description="Index (0-8) where player X wants to move.")
    mode: GameMode = Field(
        GameMode.SINGLE,
        description="Current match mode ('single' for 1 vs Computer or 'versus' for local multiplayer).",
    )
    random_seed: Optional[int] = Field(
        None, description="Optional seed for randomness to allow deterministic tests."
    )


class TurnResponse(BaseModel):
    board: List[str] = Field(..., description="Updated board after applying X and O moves.")
    o_move: int = Field(
        ..., description="Index (0-8) where computer played O, or -1 if no available cell."
    )
    status: GameOutcome = Field(
        ..., description="Current terminal status of the board after the turn."
    )
    winner: Optional[str] = Field(
        None,
        description="Winner identifier ('X', 'O', or 'draw'); null when the game is still in progress.",
    )
    is_terminal: bool = Field(..., description="True when the game has reached a win or draw state.")
    current_player: Optional[str] = Field(
        None,
        description="Next player to move when the game is still in progress; omitted otherwise.",
    )
    winning_cells: List[int] = Field(
        default_factory=list,
        description="Indices of the winning three-cell line when a player wins; empty otherwise.",
    )
    scoreboard: ScoreboardSummary | None = Field(
        None,
        description="Persistent scoreboard totals retrieved when the board is reset.",
    )
    mode: GameMode = Field(
        ..., description="Selected match mode for the current game state."
    )
