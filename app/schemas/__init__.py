"""Pydantic request and response schemas."""

from .health import HealthResponse
from .game import GameCreate, ScoreSummary, ScoreboardSummary

__all__ = ["HealthResponse", "GameCreate", "ScoreSummary", "ScoreboardSummary"]
