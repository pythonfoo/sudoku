from collections import defaultdict

from .utils import Action, Cell, Generator, group_generator


@group_generator()
def singles(field, *, type: str, idx: int, group: set[Cell]) -> Generator[Action]:
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
