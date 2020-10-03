from .cell import Cell
from .types import CellPosition
from typing import NamedTuple
from collections import defaultdict
import wrapt
import random


class Action(NamedTuple):
    action: str
    value: CellPosition
    cell: Cell
    reason: str


def group_generator(
    group_types=["row", "column", "block"], indices=[1, 2, 3, 4, 5, 6, 7, 8, 9]
):
    @wrapt.decorator
    def my_decorator(wrapped, instance, args, kwargs):
        nonlocal group_types
        nonlocal indices
        self = instance

        if "group" in kwargs:
            yield from wrapped(
                type=kwargs.get("type"),
                idx=kwargs.get("idx"),
                group=kwargs.get("group"),
            )
            return
        if "group_types" in kwargs:
            group_types = list(kwargs["group_types"])
        elif "group_type" in kwargs:
            group_types = [kwargs["group_type"]]

        if "indices" in kwargs:
            indices = list(kwargs["indices"])
        elif "idx" in kwargs:
            indices = [kwargs.pop("idx")]

        # if kwargs.get("randomize"):
        random.shuffle(group_types)
        random.shuffle(indices)

        for type in group_types:
            for idx in indices:
                group = self.get_group(type, idx)
                yield from wrapped(type=type, idx=idx, group=group, **kwargs)

    return my_decorator


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

    @group_generator()
    def show_possibles(self, *, type, idx, group):
        for member in group:
            if member.value == 0:
                continue
            for other_member in group:
                if member == other_member:
                    continue
                if member.value in other_member.hopeful:
                    yield Action(
                        action="remove_possible",
                        value=member.value,
                        cell=other_member,
                        reason=f"value {member.value} is present in the same {type} at {member.position}",
                    )

    @group_generator()
    def naked_pairs(self, *, type, idx, group):
        pairs = defaultdict(list)
        for member in group:
            if len(member.hopeful) == 2:
                pairs[tuple(sorted(member.hopeful))].append(member)
        for to_be_removed_tuple, except_members in pairs.items():
            if len(except_members) != 2:
                continue
            for member in group:
                if member in except_members:
                    continue
                for to_be_removed in to_be_removed_tuple:
                    if to_be_removed in member.hopeful:
                        yield Action(
                            action="remove_possible",
                            value=to_be_removed,
                            cell=member,
                            reason=f"naked pair in same {type} {to_be_removed_tuple!r} on {list(e.position for e in except_members)}",
                        )

    @group_generator()
    def singles(self, *, type, idx, group):
        possibilities = defaultdict(list)
        for member in group:
            for possible_number in member.hopeful:
                possibilities[possible_number].append(member)
        for single, members in possibilities.items():
            if len(members) > 1:
                continue
            yield Action(
                action="set_number",
                value=single,
                cell=members[0],
                reason=f"single {single} found in {group} at {members[0].position}",
            )

    def apply(self, action):
        if action.action == "remove_possible":
            action.cell.hopeful -= {action.value}
            action.cell._debug.append(action.reason)
        elif action.action == "set_number":
            action.cell.value = action.value

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
