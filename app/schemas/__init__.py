"""Pydantic request and response schemas."""

from .health import HealthResponse
from .game import GameCreate, ScoreSummary

__all__ = ["HealthResponse", "GameCreate", "ScoreSummary"]
