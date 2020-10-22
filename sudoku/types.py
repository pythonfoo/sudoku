from typing import Literal, NamedTuple
from pydantic import BaseModel, validator


CellValue = int  # Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]


class CellPosition(NamedTuple):
    """
    `CellPosition` is class to store the position of a cell by its `x` and `y`.
    """

    x: CellValue
    y: CellValue

    @property
    def block(self) -> CellValue:
        """
        returns the block index of this cell.
           - `0` is the top left block,
           - `2` is the top right block,
           - `4` is the center block,
           - `8` is the bottom right block.
        """
        return ((self.x) // 3) + (((self.y) // 3)) * 3

    @property
    def row(self) -> CellValue:
        """
        returns the row index of this cell.
            - 0 is the top row
            - 8 is the bottom row.
        """
        return self.y

    @property
    def column(self) -> CellValue:
        """
        returns the column index of this cell.
            - 0 is the left most column
            - 8 is the right most column.
        """
        return self.x

    @staticmethod
    def from_int(value) -> "CellPosition":
        """
        return a new `CellPosition` object with the corresponding x and y coordinates
        For each value from 0 to 80 it will be guaranteed `as_int` will return the same value.
        """
        x = value % 9
        y = value // 9
        return CellPosition(x, y)

    def as_int(self):
        """
        translates the x and y coordinates to an interger from 0 to 80
            - 0 is the first cell of the first row, or top left Cell
            - 8 is the last cell of the top row, or top righ Cell
            - 9 is the first cell of the second row
            - 80 is the last cell of the last row, or bottom right Cell
        """
        return self.y * 9 + self.x
