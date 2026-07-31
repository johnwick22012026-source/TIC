"""Main API router to include versioned or grouped routers."""
from fastapi import APIRouter

from .games import router as games_router

router = APIRouter()

# Games endpoints (create finished game, scoreboard summary, etc.)
router.include_router(games_router)
