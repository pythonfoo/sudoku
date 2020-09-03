from typing import Literal, NamedTuple

CellValue = Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]


class CellPosition(NamedTuple):
    x: CellValue
    y: CellValue

    @property
    def group(self) -> CellValue:
        return ((self.x) // 3) + (((self.y) // 3)) * 3

    @property
    def row(self) -> CellValue:
        return self.y

    @property
    def column(self) -> CellValue:
        return self.x

    @staticmethod
    def from_int(value) -> "CellPosition":
        x = value % 9
        y = value // 9
        return CellPosition(x, y)
