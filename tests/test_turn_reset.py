from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.game_result import GameOutcome, GameResult
from app.services.turn import reset_game_state

client = TestClient(app)


def _create_result(session, winner: str, status: GameOutcome, board_snapshot: str = "[]") -> GameResult:
    record = GameResult(
        winner=winner,
        status=status,
        board_snapshot=board_snapshot,
        completed_at=datetime.now(timezone.utc),
    )
    session.add(record)
    return record


@pytest.fixture(autouse=True)
def clean_database() -> None:
    session = SessionLocal()
    try:
        session.query(GameResult).delete()
        session.commit()
        yield
    finally:
        session.close()


def test_reset_game_state_service_returns_fresh_board() -> None:
    result = reset_game_state()

    assert result.board == [""] * 9
    assert result.status == GameOutcome.IN_PROGRESS
    assert result.current_player == "X"
    assert result.winner is None
    assert result.winning_cells is None
    assert result.is_terminal is False
    assert result.o_move == -1


def test_reset_endpoint_returns_clean_game_state() -> None:
    response = client.post("/api/play/reset")
    assert response.status_code == 200

    data = response.json()
    assert data["board"] == [""] * 9
    assert data["status"] == GameOutcome.IN_PROGRESS.value
    assert data["o_move"] == -1
    assert data["is_terminal"] is False
    assert data["current_player"] == "X"
    assert data.get("winner") is None
    assert data.get("winning_cells", []) == []


def test_reset_does_not_clear_scoreboard_totals() -> None:
    session = SessionLocal()
    try:
        _create_result(session, winner="X", status=GameOutcome.X_WIN)
        _create_result(session, winner="draw", status=GameOutcome.DRAW)
        session.commit()
    finally:
        session.close()

    reset_response = client.post("/api/play/reset")
    assert reset_response.status_code == 200

    scoreboard_response = client.get("/api/games/scoreboard")
    assert scoreboard_response.status_code == 200
    scoreboard = scoreboard_response.json()

    assert scoreboard["x_wins"] == 1
    assert scoreboard["o_wins"] == 0
    assert scoreboard["draws"] == 1
