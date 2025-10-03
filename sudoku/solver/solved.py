from .utils import Action, Cell, Generator, group_generator


@group_generator()
def solved(field, *, type: str, idx: int, group: set[Cell]) -> Generator[Action]:
    for member in group:
        if len(member.hopeful) == 1:
            value = list(member.hopeful)[0]
            yield Action(
                action="set_number",
                value=value,
                cell=member,
                reason=f"solved cell {value} found at {member.position}",
            )
