import random
from collections.abc import Callable, Generator
from typing import Any, cast

import wrapt

from sudoku.action import Action
from sudoku.cell import Cell
from sudoku.field import Field


def check_generator(checks: range = range(9)) -> Callable[..., Any]:
    @wrapt.decorator
    def my_decorator(
        wrapped: Callable[..., Generator[Any]],
        instance: Any,
        args: list[Any],
        kwargs: dict[str, Any],
    ) -> Generator[Any]:
        for check in checks:
            yield from wrapped(check=check)

    return cast(Callable[..., Generator], my_decorator)


def multi_group_generator(
    group_types: list[str] | None = None,
) -> Callable[..., Any]:
    if group_types is None:
        group_types = ["rows", "columns"]

    @wrapt.decorator
    def my_decorator(
        wrapped: Callable[..., Generator[Any]],
        instance: Any,
        args: list[Any],
        kwargs: dict[str, Any],
    ) -> Generator[Any]:
        local_group_types = group_types
        field = args[0]
        random.shuffle(local_group_types)

        for type in local_group_types:
            groups = [field.get_group(type[:-1], idx) for idx in range(9)]
            yield from wrapped(type=type, groups=groups, **kwargs)

    return cast(Callable[..., Generator], my_decorator)


def group_generator(
    group_types: list[str] | None = None, indices: list[int] | None = None
) -> Callable[..., Any]:
    if group_types is None:
        group_types = ["row", "column", "block"]
    if indices is None:
        indices = [0, 1, 2, 3, 4, 5, 6, 7, 8]

    @wrapt.decorator
    def my_decorator(
        wrapped: Callable[..., Generator[Any]],
        instance: Field,
        args: list[Any],
        kwargs: dict[str, Any],
    ) -> Generator[Any]:
        local_group_types = group_types
        local_indices = indices
        field = args[0]

        if "group" in kwargs:
            yield from wrapped(
                type=kwargs.get("type"),
                idx=kwargs.get("idx"),
                group=kwargs.get("group"),
            )
            return
        if "group_types" in kwargs:
            local_group_types = list(kwargs.pop("group_types"))
        elif "group_type" in kwargs:
            local_group_types = [kwargs.pop("group_type")]

        if "indices" in kwargs:
            local_indices = list(kwargs.pop("indices"))
        elif "idx" in kwargs:
            local_indices = [kwargs.pop("idx")]

        random.shuffle(local_group_types)
        random.shuffle(local_indices)

        for type in local_group_types:
            for idx in local_indices:
                group = field.get_group(type, idx)
                yield from wrapped(type=type, idx=idx, group=group, **kwargs)

    return cast(Callable[..., Generator], my_decorator)
