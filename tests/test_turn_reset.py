from fastapi.testclient import TestClient

from app.main import app
from app.models.game_result import GameOutcome
from app.services.turn import reset_game_state

client = TestClient(app)


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
