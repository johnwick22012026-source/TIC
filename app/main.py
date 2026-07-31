from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .db.init import init_db
from .api.router import router as api_router
from .schemas.health import HealthResponse

app = FastAPI(title=settings.app_name, debug=settings.debug)

# CORS - do not remove: required for the Vite dev server to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup() -> None:
    """Bootstrap or migrate the database before servicing requests."""
    init_db()

# Mount all /api routes here for versioning or future grouping
app.include_router(api_router, prefix="/api")

@app.get("/health", response_model=HealthResponse, tags=["health"])
def health() -> HealthResponse:
    """A simple health-check endpoint."""
    return HealthResponse(status="ok")
