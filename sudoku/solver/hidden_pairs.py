from collections import defaultdict

from .utils import Action, Cell, Generator, group_generator


@group_generator()
def hidden_pairs(field, *, type: str, idx: int, group: set[Cell]) -> Generator[Action]:
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
