"""
Turn resolution logic: after a valid player X move, select one random available cell for O.
This module is deterministic when provided with a seeded random.Random instance, facilitating unit testing.
"""
import random
from typing import List, Optional, Tuple


def resolve_turn(
    board: List[str], x_index: int, rand: Optional[random.Random] = None
) -> Tuple[List[str], int]:
    """
    Apply the player's X move to the board at x_index, then pick a random empty cell for O.

    Args:
        board: A list of 9 strings representing the current board; empty string for empty cells.
        x_index: The index (0-8) where X is to move.
        rand: Optional random.Random instance for deterministic choice; if None, uses module random.

    Returns:
        A tuple (new_board, o_index) where new_board is the updated board list,
        and o_index is the index where O moved, or -1 if no cells available.

    Raises:
        ValueError: If board length is not 9, x_index is out of range, or target cell is occupied.
    """
    if len(board) != 9:
        raise ValueError(f"Board must have exactly 9 cells; got {len(board)}")
    if not (0 <= x_index < 9):
        raise ValueError(f"X move index {x_index} out of range; must be 0-8")
    if board[x_index]:
        raise ValueError(f"Cell {x_index} is already occupied")

    # Use provided Random instance or the global random
    rng = rand if rand is not None else random

    # Copy board and apply X
    new_board = board.copy()
    new_board[x_index] = "X"

    # Find available cells for O
    available = [i for i, v in enumerate(new_board) if not v]
    if not available:
        # No space for O
        return new_board, -1

    o_index = rng.choice(available)
    new_board[o_index] = "O"
    return new_board, o_index
