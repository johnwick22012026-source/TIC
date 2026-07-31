"""Helpers to bootstrap the SQLite database for local development."""

from __future__ import annotations

from .base import Base
from .session import engine
from ..models import GameResult  # noqa: F401


def init_db() -> None:
    """Create the current SQLAlchemy metadata inside the configured SQLite file.

    This function is intentionally minimal to keep the initial scaffold lightweight.
    As soon as schema changes are needed, introduce Alembic (or another migration
    tool) and replace manual create_all calls with generated migrations.
    """

    Base.metadata.create_all(bind=engine)
