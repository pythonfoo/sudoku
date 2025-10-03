from __future__ import annotations

import json
from pathlib import Path

from sudoku.action import Action
from sudoku.cell import Cell
from sudoku.types import CellPosition, CellValue


class Field:
    """
    The Field is a collection of 81 cells of a sudoku puzzle.

    Is contains some methods to interact with them.
    """

    __slots__ = ["cells"]

    _groups = (
        "row",
        "column",
        "block",
    )

    def __init__(self, cell_string: str) -> None:
        self.cells: list[Cell] = [
            Cell(value=int(value), position=CellPosition.from_int(position))
            for position, value in enumerate(
                filter(lambda x: "0" <= x <= "9", cell_string)
            )
        ]

    def get_cell(self, x: int, y: int) -> Cell:
        """
        returns the Cell with the given x and y coordinate.
        """
        index = x + 9 * y
        return self.cells[index]

    def set_cell(self, x: int, y: int, value: CellValue) -> None:
        """
        Sets the value of a cell with the given x and y coordinate.
        """
        self.get_cell(x, y).value = value

    def get_group(self, type: str, idx: int) -> set[Cell]:
        """
        returns a set of cells of the same group.

        `type` is either a `row`, `column`, or `block`
        `idx` is the index of the group regarding to the :class:`sudoku.types.CellPosition`
        """
        test = {
            "row": lambda cell, idx: cell.position.row == idx,
            "column": lambda cell, idx: cell.position.column == idx,
            "block": lambda cell, idx: cell.position.block == idx,
        }[type]
        return {cell for cell in self.cells if test(cell, idx)}

    def apply(self, action: Action) -> None:
        if action.action == "remove_possible":
            action.cell.hopeful -= {action.value}
            action.cell._debug.append((action.value, action.reason))
        elif action.action == "set_number":
            action.cell.value = action.value

    def save(self, path: Path) -> None:
        cells = [
            json.dumps(
                dict(
                    value=cell.value,
                    position=cell.position.as_int(),
                    hopeful=list(cell.hopeful),
                )
            )
            for cell in self.cells
        ]
        path.write_text("\n".join(cells))

    def load(self, path: Path) -> None:
        cell_definition_lookup = dict()
        for cell_line in path.read_text().splitlines():
            cell_definiton = json.loads(cell_line)
            cell_definition_lookup[cell_definiton["position"]] = cell_definiton
        assert len(cell_definition_lookup) == 81
        for cell in self.cells:
            cell_definiton = cell_definition_lookup[cell.position.as_int()]
            cell._value = cell_definiton["value"]
            cell.hopeful |= {1, 2, 3, 4, 5, 6, 7, 8, 9}
            cell.hopeful &= set(cell_definiton["hopeful"])

    def __str__(self) -> str:
        light_row = f"+{'   +'*9}\n"
        strong_row = f"+{'---+'*9}\n"
        return (
            strong_row
            + strong_row.join(
                light_row.join(
                    f"""| {
                        " | ".join(
                            "   ".join(map(str, self.cells[x : x + 3]))
                            for x in range(y * 9, (y + 1) * 9, 3)
                        )} |\n"""
                    for y in range(z * 3, (z + 1) * 3)
                )
                for z in range(3)
            )
            + strong_row
        )
