from sudoku.chain import Chain

import pytest


def test_construct_chain():
    c = Chain()
    x, y, z = 1, 2, 3
    c.add_pair(x, y)

    assert not c.is_same_color(x, y)
    assert c.is_opposite_color(x, y)

    assert not c.is_same_color(x, z)
    assert not c.is_opposite_color(x, z)

    assert not c.is_same_color(z, y)
    assert not c.is_opposite_color(z, y)

    c.add_pair(y, z)
    assert not c.is_same_color(x, y)
    assert c.is_opposite_color(x, y)

    assert c.is_same_color(x, z)
    assert not c.is_opposite_color(x, z)

    assert not c.is_same_color(z, y)
    assert c.is_opposite_color(z, y)

    with pytest.raises(ValueError):
        c.add_pair(x, z)
