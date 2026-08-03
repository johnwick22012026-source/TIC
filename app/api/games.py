"""Router for Tic-Tac-Toe game result endpoints."""

import logging
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

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/games", tags=["games"])


@router.post("/", response_model=ScoreSummaryWithMode, status_code=status.HTTP_201_CREATED)
def post_game(
    game: GameCreate,
    db: Session = Depends(get_db),
) -> ScoreSummaryWithMode:
    """Persist a finished game result to the database."""
    logger.info(
        "API request to finalize game result: game_id=%s winner=%s mode=%s completed_at=%s",
        getattr(game, "game_id", None),
        game.winner,
        game.mode,
        game.completed_at,
    )
    try:
        summary, stored_mode = create_game_result(db, game)
        logger.info(
            "Game result persisted: winner=%s wins=%s stored_mode=%s",
            summary.winner,
            summary.wins,
            stored_mode,
        )
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
    mode: Optional[Mode] = None,
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
    mode: Optional[Mode] = None,
) -> ScoreboardSummary:
    """Return the current persistent scoreboard totals derived from stored games."""
    try:
        return get_scoreboard_totals(db, mode=mode)
    except Exception as exc:  # pragma: no cover - just in case
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to read scoreboard totals",
        )
