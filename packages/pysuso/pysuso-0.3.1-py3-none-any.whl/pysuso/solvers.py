"""Provides a collection of Sudoku solvers."""

from collections import deque

from pysuso.boards import Board, Coordinate
from pysuso.exceptions import BoardNotSolvableException, InvalidCellValueError


class BasicSolver:
    """A basic Sudoku solver using a brute force backtracking algorithm.

    This solver uses backtracking for the empty cells. Cells are processed left to right, top to
    bottom. It always picks the next higher valid value. The algorithm stops in case one valid
    solution is found. There is no check if there is another valid solution.
    """

    SQUARE_SIZE = 3
    BOARD_SIZE = 9

    def __init__(self, board: Board) -> None:
        """Configure the solver.

        Args:
            board: Board that should be solved.
        """
        self.unsolved_board = board

    def solve(self) -> Board:
        """Search a valid solution of the board and returns the filled board.

        Raises:
            BoardNotSolvableException: If no valid solution for the board is found.

        Returns:
            A board filled with a valid solution.
        """
        remaining_cells = deque([coordinate for coordinate, value in self.unsolved_board if value == 0])
        history: deque[Coordinate] = deque()
        while remaining_cells:
            current_coordinate = remaining_cells.pop()
            current_value = self.unsolved_board[current_coordinate]
            for i in range(current_value + 1, self.BOARD_SIZE + 1):
                try:
                    self.unsolved_board[current_coordinate] = i
                    history.append(current_coordinate)
                    break
                except InvalidCellValueError:
                    continue
            else:
                self.unsolved_board[current_coordinate] = 0
                remaining_cells.append(current_coordinate)
                if history:
                    latest_history_item = history.pop()
                    remaining_cells.append(latest_history_item)
                else:
                    message = "No valid solution found."
                    raise BoardNotSolvableException(message)
        return self.unsolved_board
