from collections import defaultdict
from itertools import combinations

from .utils import Action, Cell, Generator, group_generator


@group_generator()
def hidden_triples(
    field, *, type: str, idx: int, group: set[Cell]
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
            for number_to_clean in cell_to_clean.hopeful - set(possible_hidden_tripple):
                yield Action(
                    action="remove_possible",
                    value=number_to_clean,
                    cell=cell_to_clean,
                    reason=f"hidden tripple in same {type} { {possible_hidden_tripple}!r} on {list(e.position for e in cells_of_triplet)}",
                )
