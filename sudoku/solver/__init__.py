from .box_line_reduction import box_line_reduction
from .hidden_pairs import hidden_pairs
from .hidden_triples import hidden_triples
from .naked_pairs import naked_pairs
from .naked_triples import naked_triples
from .pointing_pairs import pointing_pairs
from .show_possibles import show_possibles
from .single_chains import single_chains
from .singles import singles
from .solved import solved
from .utils import Action
from .x_wing import x_wing

weighted_solvers = [
    (0, solved),
    (1, show_possibles),
    (2, singles),
    (3, naked_pairs),
    (4, naked_triples),
    (5, hidden_pairs),
    (6, hidden_triples),
    (7, pointing_pairs),
    (8, box_line_reduction),
    (9, x_wing),
    (10, single_chains),
]


all_solvers = [solver for _, solver in sorted(weighted_solvers)]

__all__ = [
    "Action",
    "all_solvers",
    "hidden_pairs",
    "naked_pairs",
    "naked_triples",
    "show_possibles",
    "weighted_solvers",
]
