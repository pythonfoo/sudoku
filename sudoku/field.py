from __future__ import annotations

import json
import random
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any, NamedTuple, cast
from collections.abc import Callable, Generator

import wrapt

from .cell import Cell
from .chain import Chain
from .types import CellPosition, CellValue


class Action(NamedTuple):
    """
    Action is a NamedTuple that contains suggested changes to a :class:`sudoku.field.Field`

    `action` is either "remove_possible" or "set_number"

    `value` is an interger from 1 to 9

    `cell` is the cell, where this action could be applied

    `reason` is a string that will be appended to the `_debug` list to cell if `action` is "remove_possible"

    """

    action: str
    value: int
    cell: Cell
    reason: str


def check_generator(checks: range = range(9)) -> Callable[..., Any]:
    @wrapt.decorator
    def my_decorator(
        wrapped: Callable[..., Generator[Any]],
        instance: Any,
        args: list[Any],
        kwargs: dict[str, Any],
    ) -> Generator[Any]:
        self = instance
        self = self
        for check in checks:
            yield from wrapped(check=check)

    return cast(Callable[..., Generator], my_decorator)


def multi_group_generator(
    group_types: list[str] | None = None,
) -> Callable[..., Any]:
    if group_types is None:
        group_types = ["rows", "columns"]

    @wrapt.decorator
    def my_decorator(
        wrapped: Callable[..., Generator[Any]],
        instance: Any,
        args: list[Any],
        kwargs: dict[str, Any],
    ) -> Generator[Any]:
        local_group_types = group_types
        self = instance

        random.shuffle(local_group_types)

        for type in local_group_types:
            groups = [self.get_group(type[:-1], idx) for idx in range(9)]
            yield from wrapped(type=type, groups=groups, **kwargs)

    return cast(Callable[..., Generator], my_decorator)


def group_generator(
    group_types: list[str] | None = None, indices: list[int] | None = None
) -> Callable[..., Any]:
    if group_types is None:
        group_types = ["row", "column", "block"]
    if indices is None:
        indices = [0, 1, 2, 3, 4, 5, 6, 7, 8]

    @wrapt.decorator
    def my_decorator(
        wrapped: Callable[..., Generator[Any]],
        instance: Field,
        args: list[Any],
        kwargs: dict[str, Any],
    ) -> Generator[Any]:
        local_group_types = group_types
        local_indices = indices
        self = instance

        if "group" in kwargs:
            yield from wrapped(
                type=kwargs.get("type"),
                idx=kwargs.get("idx"),
                group=kwargs.get("group"),
            )
            return
        if "group_types" in kwargs:
            local_group_types = list(kwargs.pop("group_types"))
        elif "group_type" in kwargs:
            local_group_types = [kwargs.pop("group_type")]

        if "indices" in kwargs:
            local_indices = list(kwargs.pop("indices"))
        elif "idx" in kwargs:
            local_indices = [kwargs.pop("idx")]

        random.shuffle(local_group_types)
        random.shuffle(local_indices)

        for type in local_group_types:
            for idx in local_indices:
                group = self.get_group(type, idx)
                yield from wrapped(type=type, idx=idx, group=group, **kwargs)

    return cast(Callable[..., Generator], my_decorator)


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

    @group_generator()
    def show_possibles(
        self, *, type: str, idx: int, group: set[Cell]
    ) -> Generator[Action]:
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
    def naked_pairs(
        self, *, type: str, idx: int, group: set[Cell]
    ) -> Generator[Action]:
        pairs: defaultdict[tuple[int, ...], list[Cell]] = defaultdict(list)
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
    def naked_triples(
        self, *, type: str, idx: int, group: set[Cell]
    ) -> Generator[Action]:
        triples: defaultdict[tuple[int, ...], list[Cell]] = defaultdict(list)
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
    def hidden_pairs(
        self, *, type: str, idx: int, group: set[Cell]
    ) -> Generator[Action]:
        pairs: defaultdict[int, set[Cell]] = defaultdict(set)
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
    def hidden_tripples(
        self, *, type: str, idx: int, group: set[Cell]
    ) -> Generator[Action]:
        tripples: defaultdict[int, set[Cell]] = defaultdict(set)
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
    def solved(
        self, *, type: str, idx: int, group: set[Cell]
    ) -> Generator[Action]:
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
    def singles(
        self, *, type: str, idx: int, group: set[Cell]
    ) -> Generator[Action]:
        possibilities: defaultdict[int, list[Cell]] = defaultdict(list)
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
    def pointing_pairs(
        self, *, type: str, idx: int, group: set[Cell]
    ) -> Generator[Action]:
        possibilities: defaultdict[int, list[Cell]] = defaultdict(list)
        for member in group:
            for possible_number in member.hopeful:
                possibilities[possible_number].append(member)

        for pointing_pair, members in possibilities.items():
            for rc in ("row", "column"):
                if (
                    len(row_or_column := {getattr(m.position, rc) for m in members})
                    == 1
                ):
                    for member in self.get_group(type=rc, idx=row_or_column.pop()):
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

    @group_generator(group_types=["row", "column"])
    def box_line_reduction(
        self, *, type: str, idx: int, group: set[Cell]
    ) -> Generator[Action]:
        possibilities: defaultdict[int, list[Cell]] = defaultdict(list)
        for member in group:
            for possible_number in member.hopeful:
                possibilities[possible_number].append(member)

        for single_box_member, members in possibilities.items():
            if len(box := {m.position.block for m in members}) == 1:
                box_id = box.pop()
                for member in self.get_group(type="block", idx=box_id):
                    if member in members:
                        continue
                    if single_box_member not in member.hopeful:
                        continue
                    yield Action(
                        action="remove_possible",
                        value=single_box_member,
                        cell=member,
                        reason=f"box reduction {single_box_member} only in box {box_id} {list(m.position for m in members)}",
                    )

    @multi_group_generator()
    def xwing(
        self, *, type: str, groups: list[set[Cell]]
    ) -> Generator[Action]:
        def decide_x_or_y(type: str) -> str:
            match type:
                case "rows":
                    return "x"
                case "columns":
                    return "y"
                case _:
                    raise ValueError(
                        f"type was {type} but can only be `row` or `column`"
                    )

        def opposite_group(type: str) -> str:
            match type:
                case "rows":
                    return "column"
                case "columns":
                    return "row"
                case _:
                    raise ValueError(
                        f"type was {type} but can only be `row` or `column`"
                    )

        possibilities: dict[
            CellValue, dict[tuple[CellValue, ...], dict[CellValue, list[Cell]]]
        ] = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        # print(f"{type} ({idx}) {list(m.value for m in group)}")
        x_or_y = decide_x_or_y(type)
        for group_idx, group in enumerate(groups):
            for member in group:
                for possible_number in member.hopeful:
                    sorted_tuple = tuple(
                        sorted(
                            getattr(m.position, x_or_y)
                            for m in group
                            if possible_number in m.hopeful
                        )
                    )
                    # print(f"{possible_number} {sorted_tuple}")
                    possibilities[possible_number][sorted_tuple][group_idx].append(
                        member
                    )

        for possible_number, lookups in possibilities.items():
            # print(f"look for {possible_number}")
            for possibility_tuple, cell_lookup in lookups.items():
                match type, possibility_tuple, list(cell_lookup.keys()):
                    case (
                        ["rows", [col_a, col_b], [row_a, row_b]]
                        | ["columns", [row_a, row_b], [col_a, col_b]]
                    ):
                        # case [[col_a,col_b], [row_a,row_b]]:
                        # print(f"{type} solution for {possible_number} found")
                        x_wing_id = f"{col_a},{row_a} {col_a},{row_b} {col_b},{row_a} {col_b},{row_b}"
                        # print(x_wing_id)
                        good_points = sum(cell_lookup.values(), start=[])
                        for bar_idx in possibility_tuple:
                            for cell in self.get_group(
                                type=opposite_group(type), idx=bar_idx
                            ):
                                if cell in good_points:
                                    continue
                                if possible_number in cell.hopeful:
                                    yield Action(
                                        action="remove_possible",
                                        value=possible_number,
                                        cell=cell,
                                        reason=f"X-Wing {x_wing_id}, {possible_number} cannot occur in other cell in this {opposite_group(type)}",
                                    )

        yield from ()

    @check_generator()
    def single_chains(self, check: int) -> Generator[Action]:
        # https://www.sudokuwiki.org/Singles_Chains
        chains: Chain[Cell] = Chain()
        for group in self._groups:
            for idx in range(9):
                possible_cells = [
                    cell
                    for cell in self.get_group(type=group, idx=idx)
                    if check in cell.hopeful
                ]
                if len(possible_cells) != 2:
                    continue
                chains.add_pair(*possible_cells)

        possible_cells = {cell for cell in self.cells if check in cell.hopeful}
        print(chains.subchains)
        for chain in chains.subchains:
            for cell in possible_cells - chain.members:
                colors_seen = {
                    chain.member_to_color[m] for m in chain.members if cell.sees(m)
                }
                if len(colors_seen) == 2:
                    yield Action(
                        action="remove_possible",
                        value=check,
                        cell=cell,
                        reason=f"single chain rule 4: {cell} sees multiple colors of chain {chain}",
                    )
                    # TODO: should we check if it is part of a chain and use this knowledge to solve other cells already?

        yield from ()

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
