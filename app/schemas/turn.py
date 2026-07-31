"""Pydantic schemas for turn-based play and reset endpoints."""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from ..models.game_result import GameOutcome
from .game import Mode


class ResetResponse(BaseModel):
    board: List[str] = Field(..., description="Current game board cells")
    status: GameOutcome = Field(..., description="Current game status")
    winning_cells: Optional[List[int]] = Field(
        None, description="Indices of winning cells if game ended"
    )
    current_player: str = Field(..., description="Player whose turn is next")
    o_move: int = Field(
        ..., description="Index of computer move or -1 if not applied"
    )
    is_terminal: bool = Field(
        ...,
        description="True if the game is in a terminal state (win or draw)",
    )
    mode: Mode = Field(
        ..., description="Mode of the match ('single' or 'versus')"
    )


class TurnRequest(BaseModel):
    board: List[str] = Field(..., description="Current game board cells")
    x_move: int = Field(..., description="Index for player X move")
    random_seed: Optional[int] = Field(
        None,
        description="Optional seed for deterministic computer move in single-player mode",
    )
    mode: Mode = Field(
        Mode.SINGLE,
        description="Mode of the match ('single' for 1 vs Computer or 'versus' for local multiplayer)",
    )


class TurnResponse(BaseModel):
    board: List[str] = Field(..., description="Updated game board cells")
    status: GameOutcome = Field(..., description="Updated game status")
    winning_cells: Optional[List[int]] = Field(
        None, description="Indices of winning cells if game ended"
    )
    current_player: str = Field(..., description="Player whose turn is next")
    o_move: int = Field(
        ..., description="Index of computer move or -1 if not applied"
    )
    is_terminal: bool = Field(
        ...,
        description="True if the game is in a terminal state (win or draw)",
    )
    mode: Mode = Field(
        ..., description="Mode of the match ('single' or 'versus')"
    )
