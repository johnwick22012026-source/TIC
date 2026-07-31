"""Router for turn-resolution endpoint: accepts a player X move and returns an O move."""
from fastapi import APIRouter, HTTPException, status
import random

from ..schemas.turn import TurnRequest, TurnResponse
from ..services.turn import resolve_turn, reset_game_state

router = APIRouter(prefix="/play", tags=["turns"])


@router.post("", response_model=TurnResponse, response_model_exclude_none=True)
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
        current_player=result.current_player,
        winning_cells=list(result.winning_cells) if result.winning_cells else [],
    )


@router.post("/reset", response_model=TurnResponse, response_model_exclude_none=True)
def reset_game_response() -> TurnResponse:
    """Return a fresh transient game state representing a new round starting with X."""
    result = reset_game_state()
    return TurnResponse(
        board=result.board,
        o_move=result.o_move,
        status=result.status,
        winner=result.winner,
        is_terminal=result.is_terminal,
        current_player=result.current_player,
        winning_cells=list(result.winning_cells) if result.winning_cells else [],
    )
