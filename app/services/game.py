"""Service layer for creating and summarizing game results."""

from datetime import datetime, timezone
from typing import List

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..models.game_result import GameOutcome, GameResult
from ..schemas.game import GameCreate, ScoreSummary, GamesSummary, ScoreboardSummary


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


def get_games_summary(db: Session) -> GamesSummary:
    """
    Query the database for total wins of player X, wins of computer O, and draws.
    Only finished games (status != IN_PROGRESS) are counted.
    """
    # Count human player (X) wins
    x_wins_stmt = select(func.count(GameResult.id)).where(GameResult.status == GameOutcome.X_WIN)
    x_wins = db.execute(x_wins_stmt).scalar_one()
    # Count computer (O) wins
    o_wins_stmt = select(func.count(GameResult.id)).where(GameResult.status == GameOutcome.O_WIN)
    o_wins = db.execute(o_wins_stmt).scalar_one()
    # Count draws
    draw_stmt = select(func.count(GameResult.id)).where(GameResult.status == GameOutcome.DRAW)
    draws = db.execute(draw_stmt).scalar_one()

    return GamesSummary(
        player_wins=int(x_wins),
        computer_wins=int(o_wins),
        draws=int(draws),
    )


def get_scoreboard_totals(db: Session) -> ScoreboardSummary:
    """Return a stable scoreboard view with X, O, and draw totals based on finished games."""
    games = get_games_summary(db)
    return ScoreboardSummary(
        x_wins=games.player_wins,
        o_wins=games.computer_wins,
        draws=games.draws,
    )
