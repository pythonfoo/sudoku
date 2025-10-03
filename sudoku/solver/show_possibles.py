from .utils import Action, Cell, Generator, group_generator


@group_generator()
def show_possibles(
    field, *, type: str, idx: int, group: set[Cell]
) -> Generator[Action]:
    """
    Show impossible values for cells in a given group (row, column, or box) and yield actions to remove them.
    """
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
