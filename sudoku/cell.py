from __future__ import annotations
from .types import CellValue, CellPosition, Set, List, Tuple


class Cell:
    __slots__ = ["_value", "position", "hopeful", "futile", "_debug"]

    def __init__(self, value: CellValue, position: CellPosition):
        self.position: CellPosition = position
        self.hopeful: Set[CellValue] = (
            {1, 2, 3, 4, 5, 6, 7, 8, 9} if value == 0 else set()
        )  # numbers that are still possible
        self.futile: Set[CellValue] = set()  # numbers that are not possible anymore
        self._debug: List[
            Tuple[CellValue, str]
        ] = list()  # list of reason why a number is not possible anymore
        self._value = value

    @property
    def value(self):
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
