"""Router for turn-resolution endpoint: accepts a player X move and returns an O move."""
from fastapi import APIRouter, HTTPException, status
import random

from ..schemas.turn import TurnRequest, TurnResponse
from ..services.turn import resolve_turn

router = APIRouter(prefix="/play", tags=["turns"])


@router.post("", response_model=TurnResponse)
def play_turn(request: TurnRequest) -> TurnResponse:
    """
    Execute a player X move and a subsequent random computer O move.

    Returns the updated board, terminal outcome, and the index of the O move.
    """
    rng = random.Random(request.random_seed) if request.random_seed is not None else None
    try:
        result = resolve_turn(request.board, request.x_move, rng)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    return TurnResponse(
        board=result.board,
        o_move=result.o_move,
        status=result.status,
        winner=result.winner,
        is_terminal=result.is_terminal,
    )
