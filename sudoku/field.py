import json
import random
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from typing import NamedTuple

import wrapt

from .cell import Cell
from .types import CellPosition


class Action(NamedTuple):
    action: str
    value: CellPosition
    cell: Cell
    reason: str


def group_generator(
    group_types=["row", "column", "block"], indices=[0, 1, 2, 3, 4, 5, 6, 7, 8]
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
            group_types = list(kwargs.pop("group_types"))
        elif "group_type" in kwargs:
            group_types = [kwargs.pop("group_type")]

        if "indices" in kwargs:
            indices = list(kwargs.pop("indices"))
        elif "idx" in kwargs:
            indices = [kwargs.pop("idx")]

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
    def naked_triples(self, *, type, idx, group):
        triples = defaultdict(list)
        for member in group:
            if len(member.hopeful) == 3:
                triples[tuple(sorted(member.hopeful))].append(member)
            if len(member.hopeful) == 2:
                for missing_value in {1, 2, 3, 4, 5, 6, 7, 8} - member.hopeful:
                    triples[tuple(sorted(member.hopeful | {missing_value}))].append(
                        member
                    )

        for to_be_removed_tuple, except_members in triples.items():
            if len(except_members) != 3:
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
                            reason=f"naked triple in same {type} {to_be_removed_tuple!r} on {list(e.position for e in except_members)}",
                        )

    @group_generator()
    def hidden_pairs(self, *, type, idx, group):
        pairs = defaultdict(set)
        for member in group:
            for possible in member.hopeful:
                pairs[possible].add(member)
        for key in list(pairs.keys()):
            if len(pairs[key]) > 2:
                del pairs[key]
        possible_hidden_pairs = list(pairs.keys())
        while possible_hidden_pairs:
            possible_hidden_pair = possible_hidden_pairs.pop()
            for other_possible_pair in possible_hidden_pairs:
                if pairs[possible_hidden_pair] == pairs[other_possible_pair]:
                    # we don't have to check this number twice
                    possible_hidden_pairs.pop(
                        possible_hidden_pairs.index(other_possible_pair)
                    )

                    for cell_to_clean in pairs[possible_hidden_pair]:
                        for number_to_clean in cell_to_clean.hopeful - {
                            possible_hidden_pair,
                            other_possible_pair,
                        }:
                            yield Action(
                                action="remove_possible",
                                value=number_to_clean,
                                cell=cell_to_clean,
                                reason=f"hidden pair in same {type} { {possible_hidden_pair, other_possible_pair}!r} on {list(e.position for e in pairs[possible_hidden_pair])}",
                            )

    @group_generator()
    def hidden_tripples(self, *, type, idx, group):
        tripples = defaultdict(set)
        for member in group:
            for possible in member.hopeful:
                tripples[possible].add(member)
        for key in list(tripples.keys()):
            if len(tripples[key]) > 3:
                del tripples[key]

        for possible_hidden_tripple in combinations(tripples.keys(), 3):
            cells_of_triplet = set()
            for possible_safe_value in possible_hidden_tripple:
                cells_of_triplet |= tripples[possible_safe_value]
            if len(cells_of_triplet) > 3:
                continue

            for cell_to_clean in cells_of_triplet:
                for number_to_clean in cell_to_clean.hopeful - set(
                    possible_hidden_tripple
                ):
                    yield Action(
                        action="remove_possible",
                        value=number_to_clean,
                        cell=cell_to_clean,
                        reason=f"hidden tripple in same {type} { {possible_hidden_tripple}!r} on {list(e.position for e in cells_of_triplet)}",
                    )

    @group_generator()
    def solved(self, *, type, idx, group):
        for member in group:
            if len(member.hopeful) == 1:
                value = list(member.hopeful)[0]
                yield Action(
                    action="set_number",
                    value=value,
                    cell=member,
                    reason=f"solved cell {value} found at {member.position}",
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
                reason=f"single {single} found in {type} at {members[0].position}",
            )

    @group_generator(group_types=["block"])
    def pointing_pairs(self, *, type, idx, group):
        possibilities = defaultdict(list)
        for member in group:
            for possible_number in member.hopeful:
                possibilities[possible_number].append(member)

        for pointing_pair, members in possibilities.items():
            for rc in ("row", "column"):
                if (
                    len(row_or_column := {getattr(m.position, rc) for m in members})
                    == 1
                ):
                    for member in self.get_group(type=rc, id=row_or_column.pop()):
                        if member in members:
                            continue
                        if pointing_pair not in member.hopeful:
                            continue
                        yield Action(
                            action="remove_possible",
                            value=pointing_pair,
                            cell=member,
                            reason=f"pointing pair {pointing_pair} in same {rc} {list(m.position for m in members)}",
                        )

    def apply(self, action):
        if action.action == "remove_possible":
            action.cell.hopeful -= {action.value}
            action.cell._debug.append(action.reason)
        elif action.action == "set_number":
            action.cell.value = action.value

    def save(self, path: Path):
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

    def load(self, path: Path):
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
