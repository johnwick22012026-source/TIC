"""Router for turn-resolution endpoint: accepts a player X move and returns an O move."""
from fastapi import APIRouter, HTTPException, status, BackgroundTasks, Query
import random
import json
from datetime import datetime, timezone

from ..schemas.turn import TurnRequest, TurnResponse
from ..services.turn import resolve_turn, reset_game_state
from ..services.game import create_game_result
from ..schemas.game import GameCreate, Mode
from ..db.session import SessionLocal
from ..models.game_result import GameMode

router = APIRouter(prefix="/play", tags=["turns"])


def _persist_game_result(winner: str, board: list[str], mode: GameMode) -> None:
    """
    Background task to persist a finished game result.
    """
    db = SessionLocal()
    try:
        board_snapshot = json.dumps(board)
        game_create = GameCreate(
            winner=winner,
            board_snapshot=board_snapshot,
            completed_at=datetime.now(timezone.utc),
            mode=Mode(mode.value),
        )
        create_game_result(db, game_create)
    except Exception:
        pass
    finally:
        db.close()


@router.post("", response_model=TurnResponse, response_model_exclude_none=True)
def play_turn(
    request: TurnRequest,
    background_tasks: BackgroundTasks,
) -> TurnResponse:
    """
    Execute a player X move and a subsequent random computer O move.

    Persist the result when the game reaches a terminal state.
    """
    rng = random.Random(request.random_seed) if request.random_seed is not None else None
    try:
        result = resolve_turn(request.board, request.x_move, request.mode, rng)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    if result.is_terminal and result.winner:
        background_tasks.add_task(_persist_game_result, result.winner, result.board, result.mode)

    return TurnResponse(
        board=result.board,
        o_move=result.o_move,
        status=result.status,
        winner=result.winner,
        is_terminal=result.is_terminal,
        current_player=result.current_player,
        winning_cells=list(result.winning_cells) if result.winning_cells else [],
        mode=result.mode,
    )


@router.post("/reset", response_model=TurnResponse, response_model_exclude_none=True)
def reset_game_response(
    mode: GameMode = Query(
        GameMode.SINGLE,
        description="Requested match mode for the upcoming game (single for 1 vs Computer).",
    )
) -> TurnResponse:
    """Return a fresh transient game state representing a new round starting with X without touching the accumulated scoreboard data."""
    result = reset_game_state(mode)
    return TurnResponse(
        board=result.board,
        o_move=result.o_move,
        status=result.status,
        winner=result.winner,
        is_terminal=result.is_terminal,
        current_player=result.current_player,
        winning_cells=list(result.winning_cells) if result.winning_cells else [],
        mode=result.mode,
    )
