"""
Turn resolution logic: after a valid player X move, select one random available cell for O.
This module is deterministic when provided with a seeded random.Random instance, facilitating unit testing.
"""
import random
from dataclasses import dataclass
from typing import List, Optional, Tuple

from ..models.game_result import GameOutcome

WIN_LINES: Tuple[Tuple[int, int, int], ...] = (
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
)


@dataclass(frozen=True)
class TurnResolution:
    board: List[str]
    o_move: int
    status: GameOutcome
    winner: Optional[str]
    is_terminal: bool
    current_player: Optional[str]
    winning_cells: Optional[Tuple[int, int, int]]


def _evaluate_board(board: List[str]) -> GameOutcome:
    for a, b, c in WIN_LINES:
        value = board[a]
        if value and value == board[b] == board[c]:
            return GameOutcome.X_WIN if value == "X" else GameOutcome.O_WIN

    if all(cell for cell in board):
        return GameOutcome.DRAW

    return GameOutcome.IN_PROGRESS


def _winner_from_status(status: GameOutcome) -> Optional[str]:
    if status == GameOutcome.X_WIN:
        return "X"
    if status == GameOutcome.O_WIN:
        return "O"
    if status == GameOutcome.DRAW:
        return "draw"
    return None


def _winning_cells(board: List[str]) -> Optional[Tuple[int, int, int]]:
    for line in WIN_LINES:
        a, b, c = line
        value = board[a]
        if value and value == board[b] == board[c]:
            return line
    return None


def _current_player_for_status(status: GameOutcome) -> Optional[str]:
    return "X" if status == GameOutcome.IN_PROGRESS else None


def resolve_turn(
    board: List[str], x_index: int, rand: Optional[random.Random] = None
) -> TurnResolution:
    """
    Apply the player's X move to the board at x_index, then pick a random empty cell for O.

    Args:
        board: A list of 9 strings representing the current board; empty string for empty cells.
        x_index: The index (0-8) where X is to move.
        rand: Optional random.Random instance for deterministic choice; if None, uses module random.

    Returns:
        A TurnResolution describing the new board state, the O move, and terminal outcome.

    Raises:
        ValueError: If board length is not 9, x_index is out of range, the target cell is occupied,
            or the provided board already represents a terminal game state.
    """
    if len(board) != 9:
        raise ValueError(f"Board must have exactly 9 cells; got {len(board)}")
    if not (0 <= x_index < 9):
        raise ValueError(f"X move index {x_index} out of range; must be 0-8")

    status_before = _evaluate_board(board)
    if status_before != GameOutcome.IN_PROGRESS:
        raise ValueError("The game is already complete; no further moves are allowed.")

    if board[x_index]:
        raise ValueError(f"Cell {x_index} is already occupied")

    rng = rand if rand is not None else random

    new_board = board.copy()
    new_board[x_index] = "X"

    status_after_x = _evaluate_board(new_board)
    winning_cells_after_x = _winning_cells(new_board)

    if status_after_x != GameOutcome.IN_PROGRESS:
        return TurnResolution(
            board=new_board,
            o_move=-1,
            status=status_after_x,
            winner=_winner_from_status(status_after_x),
            is_terminal=True,
            current_player=None,
            winning_cells=winning_cells_after_x,
        )

    available = [i for i, value in enumerate(new_board) if not value]
    if not available:
        return TurnResolution(
            board=new_board,
            o_move=-1,
            status=GameOutcome.DRAW,
            winner=_winner_from_status(GameOutcome.DRAW),
            is_terminal=True,
            current_player=None,
            winning_cells=None,
        )

    o_index = rng.choice(available)
    new_board[o_index] = "O"

    status_after_o = _evaluate_board(new_board)
    winning_cells_after_o = _winning_cells(new_board)
    is_terminal = status_after_o != GameOutcome.IN_PROGRESS

    return TurnResolution(
        board=new_board,
        o_move=o_index,
        status=status_after_o,
        winner=_winner_from_status(status_after_o),
        is_terminal=is_terminal,
        current_player=_current_player_for_status(status_after_o),
        winning_cells=winning_cells_after_o,
    )


def reset_game_state() -> TurnResolution:
    """Return a fresh, empty board with transient game state reset to the starting player."""
    empty_board = [""] * 9
    return TurnResolution(
        board=empty_board,
        o_move=-1,
        status=GameOutcome.IN_PROGRESS,
        winner=None,
        is_terminal=False,
        current_player="X",
        winning_cells=None,
    )
