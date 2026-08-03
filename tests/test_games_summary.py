from datetime import datetime, timezone
from typing import Any, Dict

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


def test_win_round_completion_produces_observable_payload() -> None:
    payload = {
        "winner": "X",
        "board_snapshot": "[\"X\", \"X\", \"X\", \"\", \"O\", \"\", \"\", \"\", \"\"]",
        "summary": {
            "winner": "X",
            "wins": 3,
        },
    }

    response = client.post("/api/games/", json=payload)
    assert response.status_code == 201

    data = response.json()
    # ScoreSummaryWithMode returns the summary for the winning player along with the persisted mode
    assert data["winner"] == "X"
    assert data["wins"] == 3
    assert data["mode"] == "single"

    session = SessionLocal()
    try:
        stmt = select(GameResult).order_by(GameResult.recorded_at.desc())
        latest = session.execute(stmt).scalar_one()
        assert latest.board_snapshot == payload["board_snapshot"]
        assert latest.status == GameOutcome.X_WIN
        assert latest.summary == payload["summary"]
    finally:
        session.close()


def test_round_persistence_via_game_flow_exposes_save_contract_failure() -> None:
    """Regression fixture: exercising the winning-round persistence flow through /api/play and into
    /api/games/ documents the current failure when the backend rejects a completed round that
    does not present the required summary data."""
    # Reset a fresh game so we begin from an empty board
    reset_response = client.post("/api/play/reset")
    assert reset_response.status_code == 200

    # Play a deterministic sequence of moves resulting in X winning across the top row.
    turn_payloads = [
        {"board": ["" ] * 9, "x_move": 0, "mode": "single", "random_seed": 1},
        {"board": ["X", "", "", "", "", "", "", "", ""], "x_move": 4, "mode": "single", "random_seed": 1},
        {"board": ["X", "", "", "", "O", "", "", "", ""], "x_move": 1, "mode": "single", "random_seed": 1},
        {"board": ["X", "X", "", "O", "O", "", "", "", ""], "x_move": 2, "mode": "single", "random_seed": 1},
    ]

    for payload in turn_payloads:
        response = client.post("/api/play", json=payload)
        assert response.status_code == 200

    # Build the save payload from the last returned state (X has won on top row)
    completed_payload = response.json()
    assert "summary" not in completed_payload

    # Attempt to persist via the real /api/games/ endpoint. The current contract rejects completed rounds without a summary status.
    # The 400 with a missing "summary" detail is the regression signal we document until the persistence path accepts
    # winning-round payloads with the expected summary field.
    save_response = client.post("/api/games/", json=completed_payload)

    assert save_response.status_code == 400
    assert "summary" in save_response.json().get("detail", "")


def _build_winning_round_payload() -> Dict[str, Any]:
    reset_response = client.post("/api/play/reset")
    assert reset_response.status_code == 200

    turn_payloads = [
        {"board": ["" for _ in range(9)], "x_move": 0, "mode": "single", "random_seed": 1},
        {"board": ["X", "", "", "", "", "", "", "", ""], "x_move": 4, "mode": "single", "random_seed": 1},
        {"board": ["X", "", "", "", "O", "", "", "", ""], "x_move": 1, "mode": "single", "random_seed": 1},
        {"board": ["X", "X", "", "O", "O", "", "", "", ""], "x_move": 2, "mode": "single", "random_seed": 1},
    ]

    last_response = None
    for payload in turn_payloads:
        response = client.post("/api/play", json=payload)
        assert response.status_code == 200
        last_response = response

    assert last_response is not None
    return last_response.json()


def test_round_completion_save_contract_accepts_expected_summary_payload() -> None:
    completed_payload = _build_winning_round_payload()
    assert "summary" not in completed_payload

    completion_summary = {"winner": "X", "wins": 3}
    completed_payload["summary"] = completion_summary

    save_response = client.post("/api/games/", json=completed_payload)
    assert save_response.status_code == 201

    data = save_response.json()
    assert data["winner"] == completion_summary["winner"]
    assert data["wins"] == completion_summary["wins"]
    assert data["mode"] == "single"
    assert {"winner", "board_snapshot", "summary"}.issubset(completed_payload.keys())


def test_round_completion_save_contract_requires_summary_field() -> None:
    completed_payload = _build_winning_round_payload()
    assert "summary" not in completed_payload

    save_response = client.post("/api/games/", json=completed_payload)
    assert save_response.status_code == 400
    assert "summary" in save_response.json().get("detail", "")


def test_round_completion_save_contract_rejects_missing_board_snapshot() -> None:
    response = client.post("/api/games/", json={"winner": "X"})
    assert response.status_code == 422

    detail = response.json().get("detail", [])
    assert any(error.get("loc", [])[-1] == "board_snapshot" for error in detail if isinstance(error, dict))
