# PySuSo

PySuSo is a library for solving Sudoku puzzels with Python.

## What does PySuSo provide

PySuSo provides a brute force backtracking solver for Sudoku puzzels. In addition to the solver a board
representing the Sudoku puzzel is provided.

## Installation

PySuSo is available on PyPi as `pysuso`. To install with `pip` run:

```
pip install pysuso
```

## Quick start

Create a board using one of the provided methods on the `Board` class. See the documentation for an overview off all
the methods.

```py
board = Board.from_list(
    [
        0, 5, 0, 7, 0, 3, 0, 6, 0,
        0, 0, 7, 0, 0, 0, 8, 0, 0,
        0, 0, 0, 8, 1, 6, 0, 0, 0,
        0, 0, 0, 0, 3, 0, 0, 0, 0,
        0, 0, 5, 0, 0, 0, 1, 0, 0,
        7, 3, 0, 0, 4, 0, 0, 8, 6,
        9, 0, 6, 0, 0, 0, 2, 0, 4,
        8, 4, 0, 5, 7, 2, 0, 9, 3,
        0, 0, 0, 4, 0, 9, 0, 0, 0
    ]
)
```

Create a solver providing the board:

```py
solver = BasicSolver(board)
```

Call the `solve` method to search for a valid solution:

```py
solver.solve()
```

Full example including imports:

```py linenums="1"
from pysuso.boards import Board
from pysuso.solvers import BasicSolver

board = Board.from_list(
    [
        0, 5, 0, 7, 0, 3, 0, 6, 0,
        0, 0, 7, 0, 0, 0, 8, 0, 0,
        0, 0, 0, 8, 1, 6, 0, 0, 0,
        0, 0, 0, 0, 3, 0, 0, 0, 0,
        0, 0, 5, 0, 0, 0, 1, 0, 0,
        7, 3, 0, 0, 4, 0, 0, 8, 6,
        9, 0, 6, 0, 0, 0, 2, 0, 4,
        8, 4, 0, 5, 7, 2, 0, 9, 3,
        0, 0, 0, 4, 0, 9, 0, 0, 0
    ]
)
solver = BasicSolver(board)
solution = solver.solve()
print(solution)
```

## Documentation

Full documentation is available at [PySuSo Documentation](https://mcneall.github.io/PySuSo/).

## Additional remarks

The tests for the solver are based on Sudokus found in the
[Sudoku Exchange Puzzle Bank](https://github.com/grantm/sudoku-exchange-puzzle-bank).