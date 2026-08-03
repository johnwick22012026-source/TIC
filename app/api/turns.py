"""Router for turn resolution and reset endpoints."""
from typing import Optional

from fastapi import APIRouter, HTTPException, status

from ..schemas.turn import ResetResponse, TurnRequest, TurnResponse
from ..schemas.game import Mode as SchemaMode
from ..services.turn import reset_game_state, play_turn

router = APIRouter(prefix="/play", tags=["turns"])


@router.post("/reset", response_model=ResetResponse)
def reset_play(
    mode: Optional[SchemaMode] = None,
) -> ResetResponse:
    """Start a fresh game state in the specified mode."""
    try:
        state = reset_game_state(mode)
        return ResetResponse(
            board=state.board,
            status=state.status,
            winning_cells=state.winning_cells or [],
            current_player=state.current_player,
            o_move=state.o_move,
            is_terminal=state.is_terminal,
            mode=SchemaMode(state.mode.value),
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to reset game state",
        )


@router.post("", response_model=TurnResponse)
def play(
    request: TurnRequest,
) -> TurnResponse:
    """Apply an X move (and O move if single-player) for the current board."""
    try:
        state = play_turn(
            board=request.board,
            x_move=request.x_move,
            mode=request.mode,
            random_seed=request.random_seed,
        )
        return TurnResponse(
            board=state.board,
            status=state.status,
            winning_cells=state.winning_cells,
            current_player=state.current_player,
            o_move=state.o_move,
            is_terminal=state.is_terminal,
            mode=SchemaMode(state.mode.value),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
