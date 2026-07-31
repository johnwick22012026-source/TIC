"""Pydantic schemas for turn resolution (player X move then random O move)."""
from typing import List, Optional
from pydantic import BaseModel, Field, conlist


class TurnRequest(BaseModel):
    board: conlist(str, min_items=9, max_items=9) = Field(
        ..., description="List of 9 cell values ('', 'X', or 'O') before the X move."
    )
    x_move: int = Field(..., ge=0, lt=9, description="Index (0-8) where player X wants to move.")
    random_seed: Optional[int] = Field(
        None, description="Optional seed for randomness to allow deterministic tests."
    )


class TurnResponse(BaseModel):
    board: List[str] = Field(..., description="Updated board after applying X and O moves.")
    o_move: int = Field(
        ..., description="Index (0-8) where computer played O, or -1 if no available cell."
    )
