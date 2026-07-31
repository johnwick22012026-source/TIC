"""Router for Tic-Tac-Toe game result endpoints."""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from ..schemas.game import GameCreate, GamesSummary, ScoreSummary, ScoreboardSummary
from ..services.game import create_game_result, get_games_summary, get_scoreboard_totals
from ..db.session import get_db

router = APIRouter(prefix="/games", tags=["games"])

@router.post("/", response_model=ScoreSummary, status_code=status.HTTP_201_CREATED)
def post_game(
    game: GameCreate,
    db: Session = Depends(get_db),
) -> ScoreSummary:
    """Persist a finished game result to the database."""
    try:
        return create_game_result(db, game)
    except NotImplementedError:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Endpoint not implemented yet",
        )

@router.get("/summary", response_model=GamesSummary)
def summary(
    db: Session = Depends(get_db),
) -> GamesSummary:
    """Retrieve aggregated scoreboard totals for player wins, computer wins, and draws."""
    try:
        return get_games_summary(db)
    except NotImplementedError:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Endpoint not implemented yet",
        )

@router.get("/scoreboard", response_model=ScoreboardSummary)
def scoreboard(
    db: Session = Depends(get_db),
) -> ScoreboardSummary:
    """Return the current persistent scoreboard totals derived from stored games."""
    try:
        return get_scoreboard_totals(db)
    except Exception as exc:  # pragma: no cover - just in case
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to read scoreboard totals",
        )
