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

    def _iterate(x: T | R, n: int) -> T | R:
        return n and _iterate(function(x, *args, **kwargs), n - 1) or x

    return _iterate(base, count)


def fallback(value: T | None, fallback_value: T) -> T:
    return fallback_value if value is None else value
