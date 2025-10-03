import pytest

from sudoku.chain import Chain


def test_construct_chain() -> None:
    c: Chain[int] = Chain()
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
        # it is not possible to add a loop that would disallow to cycle two colors after each node.
        c.add_pair(x, z)

    # but loops are possible
    w = 4
    c.add_pair(x, w)
    c.add_pair(z, w)

    assert not c.is_same_color(x, y)
    assert c.is_opposite_color(x, y)

    assert c.is_same_color(x, z)
    assert not c.is_opposite_color(x, z)

    assert not c.is_same_color(x, w)
    assert c.is_opposite_color(x, w)

    assert not c.is_same_color(z, y)
    assert c.is_opposite_color(z, y)

    assert not c.is_same_color(z, w)
    assert c.is_opposite_color(z, w)
