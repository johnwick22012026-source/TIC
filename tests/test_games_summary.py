from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.db.session import SessionLocal
from app.main import app
from app.models.game_result import GameMode, GameOutcome, GameResult

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


@pytest.fixture(autouse=True)
def clean_game_results_table() -> None:
    session = SessionLocal()
    try:
        session.execute(delete(GameResult))
        session.commit()
    finally:
        session.close()


def _latest_result_mode(session: SessionLocal) -> GameMode:
    stmt = select(GameResult).order_by(GameResult.recorded_at.desc())
    return session.execute(stmt).scalar_one().mode


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


def test_game_creation_records_overridden_mode() -> None:
    payload = {
        "winner": "X",
        "board_snapshot": "[]",
        "mode": "1 vs 1",
    }

    response = client.post("/api/games/", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["mode"] == "versus"

    session = SessionLocal()
    try:
        assert _latest_result_mode(session) == GameMode.VERSUS
        session.delete(session.execute(select(GameResult).order_by(GameResult.recorded_at.desc())).scalar_one())
        session.commit()
    finally:
        session.close()


def test_game_creation_defaults_to_single_mode() -> None:
    payload = {
        "winner": "O",
        "board_snapshot": "[]",
    }

    response = client.post("/api/games/", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["mode"] == "single"

    session = SessionLocal()
    try:
        assert _latest_result_mode(session) == GameMode.SINGLE
        session.delete(session.execute(select(GameResult).order_by(GameResult.recorded_at.desc())).scalar_one())
        session.commit()
    finally:
        session.close()


def test_game_result_response_preserves_mode_value_across_summary() -> None:
    payload = {
        "winner": "X",
        "board_snapshot": "[]",
        "mode": "versus",
    }

    response = client.post("/api/games/", json=payload)
    assert response.status_code == 201

    result = response.json()
    assert result["mode"] == "versus"

    session = SessionLocal()
    try:
        stmt = select(GameResult).order_by(GameResult.recorded_at.desc())
        record = session.execute(stmt).scalar_one()
        assert record.mode == GameMode.VERSUS
    finally:
        session.close()


def test_summary_endpoint_rebounds_mode_from_persisted_record() -> None:
    payload = {
        "winner": "O",
        "board_snapshot": "[]",
        "mode": "single",
    }

    post_response = client.post("/api/games/", json=payload)
    assert post_response.status_code == 201
    summary_response = client.get("/api/games/summary")
    assert summary_response.status_code == 200

    data = summary_response.json()
    assert data["player_wins"] == 0
    assert data["computer_wins"] == 1
    assert data["draws"] == 0

    session = SessionLocal()
    try:
        assert _latest_result_mode(session) == GameMode.SINGLE
    finally:
        session.close()
