from ..chain import Chain
from .utils import Action, Cell, Generator, check_generator


@check_generator()
def single_chains(field, check: int) -> Generator[Action]:
    # https://www.sudokuwiki.org/Singles_Chains
    chains: Chain[Cell] = Chain()
    for group in field._groups:
        for idx in range(9):
            possible_cells = [
                cell
                for cell in field.get_group(type=group, idx=idx)
                if check in cell.hopeful
            ]
            if len(possible_cells) != 2:
                continue
            chains.add_pair(*possible_cells)

    possible_cells = {cell for cell in field.cells if check in cell.hopeful}
    print(chains.subchains)
    for chain in chains.subchains:
        for cell in possible_cells - chain.members:
            colors_seen = {
                chain.member_to_color[m] for m in chain.members if cell.sees(m)
            }
            if len(colors_seen) == 2:
                yield Action(
                    action="remove_possible",
                    value=check,
                    cell=cell,
                    reason=f"single chain rule 4: {cell} sees multiple colors of chain {chain}",
                )
                # TODO: should we check if it is part of a chain and use this knowledge to solve other cells already?

    yield from ()
