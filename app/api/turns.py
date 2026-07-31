"""Router for turn-resolution endpoint: accepts a player X move and returns an O move."""
from fastapi import APIRouter, HTTPException, status, BackgroundTasks, Depends
from sqlalchemy.orm import Session
import random
import json

from ..schemas.turn import TurnRequest, TurnResponse
from ..services.turn import resolve_turn, reset_game_state
from ..services.game import create_game_result, get_scoreboard_totals
from ..schemas.game import GameCreate
from ..db.session import SessionLocal, get_db

router = APIRouter(prefix="/play", tags=["turns"])


def _persist_game_result(winner: str, board: list[str]) -> None:
    """
    Background task to persist a finished game result.
    """
    db = SessionLocal()
    try:
        # Serialize the board state and create a GameCreate schema
        board_snapshot = json.dumps(board)
        game_create = GameCreate(winner=winner, board_snapshot=board_snapshot)
        create_game_result(db, game_create)
    except Exception:
        # Swallow any errors to avoid impacting the main flow
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
        result = resolve_turn(request.board, request.x_move, rng)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    # If the game ended, persist the result asynchronously
    if result.is_terminal and result.winner:
        background_tasks.add_task(_persist_game_result, result.winner, result.board)

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
def reset_game_response(db: Session = Depends(get_db)) -> TurnResponse:
    """Return a fresh transient game state representing a new round starting with X while preserving scoreboard totals."""
    result = reset_game_state()
    scoreboard = get_scoreboard_totals(db)
    return TurnResponse(
        board=result.board,
        o_move=result.o_move,
        status=result.status,
        winner=result.winner,
        is_terminal=result.is_terminal,
        current_player=result.current_player,
        winning_cells=list(result.winning_cells) if result.winning_cells else [],
        scoreboard=scoreboard,
    )
