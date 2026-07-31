"""Main API router to include versioned or grouped routers."""
from fastapi import APIRouter

from .games import router as games_router
from .turns import router as turns_router

router = APIRouter()

# Games endpoints (create finished game, scoreboard summary, etc.)
router.include_router(games_router)
# Turn-resolution endpoint (player X move then random O move)
router.include_router(turns_router)
