from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.game_result import GameOutcome, GameResult
from app.services.turn import reset_game_state

client = TestClient(app)


def _create_result(
    session: SessionLocal,
    winner: str,
    status: GameOutcome,
    board_snapshot: str = "[]",
) -> GameResult:
    record = GameResult(
        winner=winner,
        status=status,
        board_snapshot=board_snapshot,
        completed_at=datetime.now(timezone.utc),
    )
    session.add(record)
    return record


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


def test_scoreboard_persists_after_reset() -> None:
    session = SessionLocal()
    try:
        _create_result(session, winner="X", status=GameOutcome.X_WIN)
        _create_result(session, winner="O", status=GameOutcome.O_WIN)
        _create_result(session, winner="draw", status=GameOutcome.DRAW)
        session.commit()
    finally:
        session.close()

    expected_summary = {"player_wins": 1, "computer_wins": 1, "draws": 1}
    expected_scoreboard = {"x_wins": 1, "o_wins": 1, "draws": 1}

    summary_before = client.get("/api/games/summary")
    assert summary_before.status_code == 200
    assert summary_before.json() == expected_summary

    scoreboard_before = client.get("/api/games/scoreboard")
    assert scoreboard_before.status_code == 200
    assert scoreboard_before.json() == expected_scoreboard

    response = client.post("/api/play/reset")
    assert response.status_code == 200

    summary_after = client.get("/api/games/summary")
    assert summary_after.status_code == 200
    assert summary_after.json() == expected_summary

    scoreboard_after = client.get("/api/games/scoreboard")
    assert scoreboard_after.status_code == 200
    assert scoreboard_after.json() == expected_scoreboard
