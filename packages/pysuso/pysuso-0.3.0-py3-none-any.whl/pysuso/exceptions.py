"""Contains expections specific to PySuSo."""


class InvalidBoardError(ValueError):
    """Raised in case the board cannot be created from the provided values."""


class InvalidCellValueError(ValueError):
    """Raised in case a value is not allowed in a cell."""


class InvalidIndexError(ValueError):
    """Raised in case an index is not valid."""


class BoardNotSolvableException(Exception):
    """Raised in case the board does not have a solution."""
