from __future__ import annotations

from typing import List, Set, Tuple

from .types import CellPosition, CellValue


class Cell:
    """
    The Cell stores the value of a cell, its position, possible values and contains
    list of reasons why a number is not possible anymore.

    It is not aware of any other Cell.

    `hopeful` is a set of all possible values that this cell could have in the future.

    `_debug` is a list of strings that explain why certain numbers are not possible anymore.
    """

    __slots__ = ["_value", "_position", "hopeful", "futile", "_debug"]

    def __init__(self, value: CellValue, position: CellPosition):
        self._position: CellPosition = position
        self.hopeful: set[CellValue] = (
            {1, 2, 3, 4, 5, 6, 7, 8, 9} if value == 0 else set()
        )  # numbers that are still possible
        self.futile: set[CellValue] = set()  # numbers that are not possible anymore
        self._debug: list[
            tuple[CellValue, str]
        ] = list()  # list of reason why a number is not possible anymore
        self._value = value

    @property
    def position(self):
        """
        represents the position of the cell

        has sub properties for
        - row
        - column
        - block
        """
        return self._position

    @property
    def value(self):
        """
        represents the cell value
         - value is 0 when the cell is not set
         - otherwise it can be any number from 1 to 9

        When the cell value will be set:

        It will raise an AssertionError when the value is not in self.hopeful
        It will raise an AssertionError when the value is in self.futile

        It cannot be set to 0 after a value has been asigned. You need to use
        the private property `_value` the change it.

        After the value has been asigned, the hopeful set will be cleared.
        """
        return self._value

    @value.setter
    def value(self, value):
        assert value in self.hopeful, f"Cell {self.position} can't be set to {value}"
        assert value not in self.futile, f"Cell {self.position} can't be set to {value}"
        self._value = value
        self.hopeful = set()

    def __str__(self):
        return f"{self._value}"

    def __repr__(self):
        return f"Cell(position={self.position}, value={self._value!r}, hopeful={self.hopeful}, futile={self.futile}, )"

    def __lt__(self, other):
        return self.position.as_int() < other.position.as_int()
