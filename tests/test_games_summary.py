from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.game_result import GameOutcome, GameResult

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


def test_summary_returns_zero_totals_when_no_finished_games_exist() -> None:
    response = client.get("/api/games/summary")
    assert response.status_code == 200

    data = response.json()
    assert data["player_wins"] == 0
    assert data["computer_wins"] == 0
    assert data["draws"] == 0


def test_summary_counts_multiple_finished_game_outcomes() -> None:
    session = SessionLocal()
    try:
        _create_result(session, winner="X", status=GameOutcome.X_WIN, board_snapshot="[\"X\"]")
        _create_result(session, winner="X", status=GameOutcome.X_WIN, board_snapshot="[\"X\"]")
        _create_result(session, winner="O", status=GameOutcome.O_WIN, board_snapshot="[\"O\"]")
        _create_result(session, winner="draw", status=GameOutcome.DRAW, board_snapshot="[\"draw\"]")
        _create_result(session, winner="draw", status=GameOutcome.DRAW, board_snapshot="[\"draw\"]")
        session.commit()
    finally:
        session.close()

    response = client.get("/api/games/summary")
    assert response.status_code == 200

    data = response.json()
    assert data["player_wins"] == 2
    assert data["computer_wins"] == 1
    assert data["draws"] == 2


def test_summary_ignores_unfinished_games() -> None:
    session = SessionLocal()
    try:
        _create_result(session, winner="X", status=GameOutcome.IN_PROGRESS, board_snapshot="[\"\"]")
        _create_result(session, winner="O", status=GameOutcome.O_WIN, board_snapshot="[\"O\"]")
        session.commit()
    finally:
        session.close()

    response = client.get("/api/games/summary")
    assert response.status_code == 200

    data = response.json()
    assert data["player_wins"] == 0
    assert data["computer_wins"] == 1
    assert data["draws"] == 0


def test_scoreboard_returns_zero_totals_when_no_games_exist() -> None:
    response = client.get("/api/games/scoreboard")
    assert response.status_code == 200

    data = response.json()
    assert data == {"x_wins": 0, "o_wins": 0, "draws": 0}


def test_scoreboard_reflects_persisted_game_totals() -> None:
    session = SessionLocal()
    try:
        _create_result(session, winner="X", status=GameOutcome.X_WIN, board_snapshot="[\"X\"]")
        _create_result(session, winner="O", status=GameOutcome.O_WIN, board_snapshot="[\"O\"]")
        _create_result(session, winner="draw", status=GameOutcome.DRAW, board_snapshot="[\"draw\"]")
        _create_result(session, winner="X", status=GameOutcome.X_WIN, board_snapshot="[\"X\"]")
        session.commit()
    finally:
        session.close()

    response = client.get("/api/games/scoreboard")
    assert response.status_code == 200

    data = response.json()
    assert data["x_wins"] == 2
    assert data["o_wins"] == 1
    assert data["draws"] == 1
