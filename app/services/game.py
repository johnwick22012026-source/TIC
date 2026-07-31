"""Service layer for creating and summarizing game results."""

from datetime import datetime, timezone
from typing import List

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..models.game_result import GameOutcome, GameResult
from ..schemas.game import GameCreate, ScoreSummary


def _status_for_winner(winner: str) -> GameOutcome:
    normalized = winner.strip().lower()
    if normalized == "x":
        return GameOutcome.X_WIN
    if normalized == "o":
        return GameOutcome.O_WIN
    if normalized == "draw":
        return GameOutcome.DRAW
    return GameOutcome.IN_PROGRESS


def _summary_for_winner(db: Session, winner: str) -> ScoreSummary:
    stmt = (
        select(func.count(GameResult.id))
        .where(GameResult.winner == winner)
        .label("wins")
    )
    wins = db.execute(stmt).scalar_one()
    return ScoreSummary(winner=winner, wins=int(wins))


def create_game_result(db: Session, game: GameCreate) -> ScoreSummary:
    """
    Persist a completed game result and return the updated scoreboard entry for the winner.
    """
    completed_at = game.completed_at or datetime.now(timezone.utc)
    status = _status_for_winner(game.winner)

    record = GameResult(
        winner=game.winner,
        status=status,
        board_snapshot=game.board_snapshot,
        summary=game.summary,
        completed_at=completed_at,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return _summary_for_winner(db, game.winner)


def get_score_summary(db: Session) -> List[ScoreSummary]:
    """
    Query the database for aggregated wins per player.
    """
    stmt = (
        select(GameResult.winner, func.count(GameResult.id).label("wins"))
        .group_by(GameResult.winner)
        .order_by(func.count(GameResult.id).desc())
    )
    rows = db.execute(stmt).all()
    return [ScoreSummary(winner=row[0], wins=int(row[1])) for row in rows]
