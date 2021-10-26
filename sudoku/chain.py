from __future__ import annotations
from collections import defaultdict
from typing import TypeVar, Generic, TypedDict, Literal

T = TypeVar("T")


class SubChain(Generic[T]):
    def __init__(self, a: T, b: T):
        self.members: set[T] = set((a, b))
        self.connections: dict[T, set[T]] = defaultdict(set)
        self.connections[a].add(b)
        self.connections[b].add(a)
        self.colors: dict[str, set[T]] = dict(a={a}, b={b})
        self.member_to_color: dict[T, Literal["a", "b"]] = {a: "a", b: "b"}

    def is_same_color(self, a: T, b: T):
        if not a in self.members or b not in self.members:
            raise ValueError("Both members have to belong to the same SubChain")
        return self.member_to_color[a] == self.member_to_color[b]

    def merge(self, other: SubChain[T]) -> None:
        union = self.members & other.members
        first_member = union.pop()
        if self.member_to_color[first_member] == other.member_to_color[first_member]:
            # all members should have the same color
            if not all(
                self.member_to_color[m] == other.member_to_color[m] for m in union
            ):
                raise ValueError("Trying to merge Chains with mixed colours")
            color_map = dict(
                a="a",
                b="b",
            )
        else:
            # no member should share the same color
            if not all(
                self.member_to_color[m] != other.member_to_color[m] for m in union
            ):
                raise ValueError("Trying to merge Chains with mixed colours")

            color_map = dict(
                a="b",
                b="a",
            )
        for source, destinations in other.connections.items():
            self.connections[source] |= destinations
        self.members |= other.members
        for other_member in other.members:
            new_color = color_map[other.member_to_color[other_member]]
            self.colors[new_color].add(other_member)
            self.member_to_color[other_member] = new_color


class Chain(Generic[T]):
    def __init__(
        self,
    ):
        self.members: set[T] = set()
        self.member_to_subchain = dict()

    def add_pair(self, a: T, b: T):
        sub_chain: SubChain[T] = SubChain(a, b)
        if a in self.members:
            sub_chain.merge(self.member_to_subchain[a])
        if b in self.members:
            sub_chain.merge(self.member_to_subchain[b])
        self.members |= sub_chain.members
        for member in sub_chain.members:
            self.member_to_subchain[member] = sub_chain

    def _is_same_subchain(self, a: T, b: T):
        if not a in self.members or b not in self.members:
            return False
        if self.member_to_subchain[a] is not self.member_to_subchain[b]:
            return False
        return True

    def is_same_color(self, a: T, b: T):
        if not self._is_same_subchain(a, b):
            return False
        return self.member_to_subchain[a].is_same_color(a, b)

    def is_opposite_color(self, a: T, b: T):
        if not self._is_same_subchain(a, b):
            return False
        return not self.is_same_color(a, b)
