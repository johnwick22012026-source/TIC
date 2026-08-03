"""Service layer for creating and summarizing game results."""

import logging
from datetime import datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..models.game_result import GameOutcome, GameMode, GameResult
from ..schemas.game import GameCreate, Mode, ScoreSummary, GamesSummary, ScoreboardSummary


_MODE_TO_GAME_MODE = {
    Mode.SINGLE: GameMode.SINGLE,
    Mode.VERSUS: GameMode.VERSUS,
}
_GAME_MODE_TO_MODE = {value: key for key, value in _MODE_TO_GAME_MODE.items()}

logger = logging.getLogger(__name__)

def _status_for_winner(winner: str) -> GameOutcome:
    """
    Determine the GameOutcome enum from a winner string.
    Raises ValueError for invalid winner values.
    """
    normalized = winner.strip().lower()
    if normalized == "x":
        return GameOutcome.X_WIN
    if normalized == "o":
        return GameOutcome.O_WIN
    if normalized == "draw":
        return GameOutcome.DRAW
    raise ValueError(f"Invalid winner '{winner}'. Must be one of 'x', 'o', or 'draw'.")


def _summary_for_winner(db: Session, winner: str) -> ScoreSummary:
    stmt = (
        select(func.count(GameResult.id).label("wins"))
        .where(GameResult.winner == winner)
    )
    wins = db.execute(stmt).scalar_one()
    return ScoreSummary(winner=winner, wins=int(wins))


def _game_mode_for_selection(mode: Optional[Mode]) -> GameMode:
    if mode is None:
        return GameMode.SINGLE
    return _MODE_TO_GAME_MODE.get(mode, GameMode.SINGLE)


def create_game_result(db: Session, game: GameCreate) -> Tuple[ScoreSummary, Mode]:
    """
    Persist a completed game result and return the updated scoreboard entry for the winner.
    Raises ValueError for invalid winner inputs.
    """
    completed_at = game.completed_at or datetime.now(timezone.utc)
    status = _status_for_winner(game.winner)
    mode = _game_mode_for_selection(game.mode)
    game_id = getattr(game, "game_id", None)
    logger.info(
        "Finalizing round: game_id=%s winner=%s mode=%s status=%s completed_at=%s summary=%s",
        game_id,
        game.winner,
        mode,
        status,
        completed_at,
        game.summary,
    )

    record = GameResult(
        winner=game.winner,
        status=status,
        mode=mode,
        board_snapshot=game.board_snapshot,
        summary=game.summary,
        completed_at=completed_at,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    stored_mode = _GAME_MODE_TO_MODE.get(record.mode, Mode.SINGLE)
    logger.info(
        "Persisted game result: id=%s winner=%s status=%s mode=%s stored_mode=%s",
        record.id,
        record.winner,
        record.status,
        record.mode,
        stored_mode,
    )
    return _summary_for_winner(db, game.winner), stored_mode

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


def get_games_summary(db: Session, mode: Optional[Mode] = None) -> GamesSummary:
    """
    Query the database for total wins of player X, wins of computer O, and draws.
    If a mode is specified, only finished games for that mode are counted;
    otherwise, games across all modes are aggregated.
    Finished games are those with status != IN_PROGRESS.
    """
    filters = [GameResult.status != GameOutcome.IN_PROGRESS]
    response_mode = mode

    if mode is not None:
        resolved_mode = _MODE_TO_GAME_MODE.get(mode, GameMode.SINGLE)
        filters.append(GameResult.mode == resolved_mode)

    x_wins_stmt = select(func.count(GameResult.id)).where(
        GameResult.status == GameOutcome.X_WIN,
        *filters
    )
    x_wins = db.execute(x_wins_stmt).scalar_one()

    o_wins_stmt = select(func.count(GameResult.id)).where(
        GameResult.status == GameOutcome.O_WIN,
        *filters
    )
    o_wins = db.execute(o_wins_stmt).scalar_one()

    draw_stmt = select(func.count(GameResult.id)).where(
        GameResult.status == GameOutcome.DRAW,
        *filters
    )
    draws = db.execute(draw_stmt).scalar_one()

    return GamesSummary(
        player_wins=int(x_wins),
        computer_wins=int(o_wins),
        draws=int(draws),
        mode=response_mode,
    )


def get_scoreboard_totals(db: Session, mode: Optional[Mode] = None) -> ScoreboardSummary:
    """Return a stable scoreboard view with X, O, and draw totals based on finished games for an optional mode."""
    games = get_games_summary(db, mode=mode)
    return ScoreboardSummary(
        x_wins=games.player_wins,
        o_wins=games.computer_wins,
        draws=games.draws,
        mode=mode,
    )
