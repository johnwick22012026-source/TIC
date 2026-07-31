"""Service layer for turn-based play logic and game resets."""
import random
from typing import List, Optional

from ..models.game_result import GameMode as PersistedGameMode, GameOutcome
from ..schemas.game import Mode
from .game import _game_mode_for_selection


# Winning lines for a 3 × 3 grid
_WIN_LINES: List[tuple[int, int, int]] = [
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
]


def _evaluate_board(cells: List[str]) -> GameOutcome:
    for a, b, c in _WIN_LINES:
        value = cells[a]
        if value and value == cells[b] and value == cells[c]:
            return GameOutcome.X_WIN if value == "X" else GameOutcome.O_WIN
    if all(cells):
        return GameOutcome.DRAW
    return GameOutcome.IN_PROGRESS


def _find_winning_cells(cells: List[str]) -> Optional[List[int]]:
    for a, b, c in _WIN_LINES:
        value = cells[a]
        if value and value == cells[b] and value == cells[c]:
            return [a, b, c]
    return None


def _validate_board(board: List[str]) -> None:
    if len(board) != 9:
        raise ValueError("Board must contain 9 cells.")
    for idx, cell in enumerate(board):
        if cell not in ("", "X", "O"):
            raise ValueError(f"Invalid value at board index {idx}: {cell}")


def _validate_move(board: List[str], x_move: int) -> None:
    if not isinstance(x_move, int):
        raise ValueError("Move index must be an integer.")
    if x_move < 0 or x_move >= len(board):
        raise ValueError(f"Move index {x_move} out of bounds.")
    if board[x_move]:
        raise ValueError(f"Cell {x_move} is already occupied.")


class TurnState:
    """Internal state representation for a single play/reset cycle."""

    def __init__(
        self,
        board: List[str],
        status: GameOutcome,
        current_player: str,
        o_move: int,
        winning_cells: Optional[List[int]] = None,
        mode: PersistedGameMode = PersistedGameMode.SINGLE,
    ):
        self.board = board
        self.status = status
        self.winner = (
            "X"
            if status == GameOutcome.X_WIN
            else "O"
            if status == GameOutcome.O_WIN
            else "draw"
            if status == GameOutcome.DRAW
            else None
        )
        self.winning_cells = winning_cells
        self.is_terminal = status != GameOutcome.IN_PROGRESS
        self.current_player = current_player
        self.o_move = o_move
        self.mode = mode


def reset_game_state(mode: Optional[Mode] = None) -> TurnState:
    """
    Return a fresh board state for a new match in the selected mode.
    """
    game_mode = _game_mode_for_selection(mode)
    return TurnState(
        board=[""] * 9,
        status=GameOutcome.IN_PROGRESS,
        current_player="X",
        o_move=-1,
        mode=game_mode,
    )


def play_turn(
    board: List[str],
    x_move: int,
    mode: Optional[Mode] = None,
    random_seed: Optional[int] = None,
) -> TurnState:
    """
    Apply the X move and, if in single-player mode, a random O move.
    """
    _validate_board(board)
    _validate_move(board, x_move)

    game_mode = _game_mode_for_selection(mode)
    # Player X move
    board_after_x = list(board)
    board_after_x[x_move] = "X"
    status_after_x = _evaluate_board(board_after_x)
    winning_after_x = (
        _find_winning_cells(board_after_x)
        if status_after_x != GameOutcome.IN_PROGRESS
        else None
    )

    # Terminal after X
    if status_after_x != GameOutcome.IN_PROGRESS:
        return TurnState(
            board=board_after_x,
            status=status_after_x,
            current_player="X",
            o_move=-1,
            winning_cells=winning_after_x,
            mode=game_mode,
        )

    # Single-player: computer O move
    if game_mode == PersistedGameMode.SINGLE:
        if random_seed is not None:
            random.seed(random_seed)
        available = [i for i, v in enumerate(board_after_x) if not v]
        if available:
            o_index = random.choice(available)
            board_after_x[o_index] = "O"
            o_move = o_index
        else:
            o_move = -1
        status_after_o = _evaluate_board(board_after_x)
        winning_after_o = (
            _find_winning_cells(board_after_x)
            if status_after_o != GameOutcome.IN_PROGRESS
            else None
        )
        return TurnState(
            board=board_after_x,
            status=status_after_o,
            current_player="X",
            o_move=o_move,
            winning_cells=winning_after_o,
            mode=game_mode,
        )

    # Versus mode: pass turn to O without computer move
    return TurnState(
        board=board_after_x,
        status=status_after_x,
        current_player="O",
        o_move=-1,
        winning_cells=winning_after_x,
        mode=game_mode,
    )
