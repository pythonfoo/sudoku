from collections import defaultdict

from .utils import Action, Cell, Generator, group_generator


@group_generator()
def naked_pairs(field, *, type: str, idx: int, group: set[Cell]) -> Generator[Action]:
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
