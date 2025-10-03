from collections import defaultdict

from .utils import Action, Cell, Generator, group_generator


@group_generator()
def naked_triples(field, *, type: str, idx: int, group: set[Cell]) -> Generator[Action]:
    triples: defaultdict[tuple[int, ...], list[Cell]] = defaultdict(list)
    for member in group:
        if len(member.hopeful) == 3:
            triples[tuple(sorted(member.hopeful))].append(member)
        if len(member.hopeful) == 2:
            for missing_value in {1, 2, 3, 4, 5, 6, 7, 8} - member.hopeful:
                triples[tuple(sorted(member.hopeful | {missing_value}))].append(member)

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
