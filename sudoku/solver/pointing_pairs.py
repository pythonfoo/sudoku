from collections import defaultdict

from .utils import Action, Cell, Generator, group_generator


@group_generator(group_types=["block"])
def pointing_pairs(
    field, *, type: str, idx: int, group: set[Cell]
) -> Generator[Action]:
    possibilities: defaultdict[int, list[Cell]] = defaultdict(list)
    for member in group:
        for possible_number in member.hopeful:
            possibilities[possible_number].append(member)

    for pointing_pair, members in possibilities.items():
        for rc in ("row", "column"):
            if len(row_or_column := {getattr(m.position, rc) for m in members}) == 1:
                for member in field.get_group(type=rc, idx=row_or_column.pop()):
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
