"""Router for Tic-Tac-Toe game result endpoints."""

from typing import Optional

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from ..schemas.game import (
    GameCreate,
    GamesSummary,
    ScoreSummaryWithMode,
    ScoreboardSummary,
    Mode,
)
from ..services.game import (
    create_game_result,
    get_games_summary,
    get_scoreboard_totals,
)
from ..db.session import get_db

router = APIRouter(prefix="/games", tags=["games"])


@router.post("/", response_model=ScoreSummaryWithMode, status_code=status.HTTP_201_CREATED)
def post_game(
    game: GameCreate,
    db: Session = Depends(get_db),
) -> ScoreSummaryWithMode:
    """Persist a finished game result to the database."""
    try:
        summary, stored_mode = create_game_result(db, game)
        return ScoreSummaryWithMode(**summary.dict(), mode=stored_mode)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except NotImplementedError:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Endpoint not implemented yet",
        )


@router.get("/summary", response_model=GamesSummary)
def summary(
    db: Session = Depends(get_db),
    mode: Optional[Mode] = Mode.SINGLE,
) -> GamesSummary:
    """Retrieve aggregated scoreboard totals for player wins, computer wins, and draws."""
    try:
        return get_games_summary(db, mode=mode)
    except NotImplementedError:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Endpoint not implemented yet",
        )


@router.get("/scoreboard", response_model=ScoreboardSummary)
def scoreboard(
    db: Session = Depends(get_db),
    mode: Optional[Mode] = Mode.SINGLE,
) -> ScoreboardSummary:
    """Return the current persistent scoreboard totals derived from stored games."""
    try:
        return get_scoreboard_totals(db, mode=mode)
    except Exception as exc:  # pragma: no cover - just in case
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to read scoreboard totals",
        )
