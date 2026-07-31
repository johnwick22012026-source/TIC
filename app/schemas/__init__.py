"""Pydantic request and response schemas."""

from .health import HealthResponse
from .game import (
    GameCreate,
    ScoreSummary,
    ScoreSummaryWithMode,
    ScoreboardSummary,
    Mode,
    GameResultResponse,
)

__all__ = [
    "HealthResponse",
    "GameCreate",
    "ScoreSummary",
    "ScoreSummaryWithMode",
    "ScoreboardSummary",
    "Mode",
    "GameResultResponse",
]
