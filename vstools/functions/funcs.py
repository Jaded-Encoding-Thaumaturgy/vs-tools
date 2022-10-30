from __future__ import annotations

from typing import Callable, Concatenate

from ..types import P, R, T

__all__ = [
    'iterate', 'fallback'
]


def iterate(
    base: T, function: Callable[Concatenate[T | R, P], T | R],
    count: int, *args: P.args, **kwargs: P.kwargs
) -> T | R:
    if count <= 0:
        return base

    result: T | R = base

    for _ in range(count):
        result = function(result, *args, **kwargs)

    return result


def fallback(value: T | None, fallback_value: T) -> T:
    return fallback_value if value is None else value
