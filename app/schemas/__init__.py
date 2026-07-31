"""Pydantic request and response schemas."""

from .health import HealthResponse
from .game import GameCreate, ScoreSummary, ScoreboardSummary, Mode, GameResultResponse

__all__ = [
    "HealthResponse",
    "GameCreate",
    "ScoreSummary",
    "ScoreboardSummary",
    "Mode",
    "GameResultResponse",
]
