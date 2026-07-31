"""Service layer for creating and summarizing game results."""

from typing import List
from sqlalchemy.orm import Session

from ..schemas.game import GameCreate, ScoreSummary
from ..models.game_result import GameResult


def create_game_result(db: Session, game: GameCreate) -> ScoreSummary:
    """
    Persist a completed game result and return the updated scoreboard entry for the winner.
    """
    # TODO: Implement actual DB insert and aggregation logic.
    raise NotImplementedError


def get_score_summary(db: Session) -> List[ScoreSummary]:
    """
    Query the database for aggregated wins per player.
    """
    # TODO: Implement actual DB query for scoreboard totals.
    raise NotImplementedError
