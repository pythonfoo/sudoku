from sudoku.cell import Cell
from sudoku.types import CellPosition


def test_cell() -> None:
    c = Cell(0, CellPosition(0, 0))
    del c
