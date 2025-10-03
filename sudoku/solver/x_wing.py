from collections import defaultdict

from ..types import CellValue
from .utils import Action, Cell, Generator, multi_group_generator


@multi_group_generator()
def x_wing(field, *, type: str, groups: list[set[Cell]]) -> Generator[Action]:
    def decide_x_or_y(type: str) -> str:
        match type:
            case "rows":
                return "x"
            case "columns":
                return "y"
            case _:
                raise ValueError(f"type was {type} but can only be `row` or `column`")

    def opposite_group(type: str) -> str:
        match type:
            case "rows":
                return "column"
            case "columns":
                return "row"
            case _:
                raise ValueError(f"type was {type} but can only be `row` or `column`")

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
                possibilities[possible_number][sorted_tuple][group_idx].append(member)

    for possible_number, lookups in possibilities.items():
        # print(f"look for {possible_number}")
        for possibility_tuple, cell_lookup in lookups.items():
            match type, possibility_tuple, list(cell_lookup.keys()):
                case ["rows", [col_a, col_b], [row_a, row_b]] | [
                    "columns",
                    [row_a, row_b],
                    [col_a, col_b],
                ]:
                    # case [[col_a,col_b], [row_a,row_b]]:
                    # print(f"{type} solution for {possible_number} found")
                    x_wing_id = f"{col_a},{row_a} {col_a},{row_b} {col_b},{row_a} {col_b},{row_b}"
                    # print(x_wing_id)
                    good_points = sum(cell_lookup.values(), start=[])
                    for bar_idx in possibility_tuple:
                        for cell in field.get_group(
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
