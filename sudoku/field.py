from .cell import Cell
from .types import CellPosition
from typing import NamedTuple


class Action(NamedTuple):
    action: str
    value: CellPosition
    cell: Cell
    reason: str


class Field:

    __slots__ = ["cells"]

    def __init__(self, cell_string: str):
        self.cells = [
            Cell(value=int(value), position=CellPosition.from_int(position))
            for position, value in enumerate(
                filter(lambda x: "0" <= x <= "9", cell_string)
            )
        ]

    def get_cell(self, x, y):
        index = x + 9 * y
        return self.cells[index]

    def set_cell(self, x, y, value):
        self.get_cell(x, y).value = value

    def get_group(self, type, id):
        test = {
            "row": lambda cell, id: cell.position.row == id,
            "column": lambda cell, id: cell.position.column == id,
            "block": lambda cell, id: cell.position.group == id,
        }[type]
        return {cell for cell in self.cells if test(cell, id)}

    def show_possibles(self):
        actions = []
        for type in ["row", "column", "block"]:
            for idx in range(9):
                group = self.get_group(type, idx)
                for member in group:
                    if member.value == 0:
                        continue
                    for other_member in group:
                        if member == other_member:
                            continue
                        if member.value in other_member.hopeful:
                            actions.append(
                                Action(
                                    action="remove_possible",
                                    value=member.value,
                                    cell=other_member,
                                    reason=f"value {member.value} is present in the same {type} at {member.position}",
                                )
                            )
        return actions

    def apply(self, actions):
        for action in actions:
            if action.action == "remove_possible":
                action.cell.hopeful -= {action.value}
                action.cell._debug.append(action.reason)

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
