from collections import defaultdict

from .utils import Action, Cell, Generator, group_generator


@group_generator(group_types=["row", "column"])
def box_line_reduction(
    field, *, type: str, idx: int, group: set[Cell]
) -> Generator[Action]:
    possibilities: defaultdict[int, list[Cell]] = defaultdict(list)
    for member in group:
        for possible_number in member.hopeful:
            possibilities[possible_number].append(member)

    for single_box_member, members in possibilities.items():
        if len(box := {m.position.block for m in members}) == 1:
            box_id = box.pop()
            for member in field.get_group(type="block", idx=box_id):
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
