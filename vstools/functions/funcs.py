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
    """
    Execute a given function over the clip multiple times.

    Different from regular iteration functions is that you do not need to pass a partial object.
    This function accepts *args and **kwargs. These will be passed on to the given function.

    Examples:

    .. code-block:: python

        >>> def double(x: int) -> int:
        ...    return x * 2
        ...
        >>> iterate(5, double, 2)
        20

        >>> iterate(clip, core.std.Maximum, 3, threshold=0.5)

    :param base:        Base clip, value, etc. to iterate over.
    :param function:    Function to iterate over the base.
    :param count:       Number of times to execute function.
    :param *args:       Positional arguments to pass to the given function.
    :param **kwargs:    Keyword arguments to pass to the given function.

    :return:            Clip, value, etc. with the given function run over it
                        *n* amount of times based on the given count.
    """
    if count <= 0:
        return base

    def _iterate(x: T | R, n: int) -> T | R:
        return n and _iterate(function(x, *args, **kwargs), n - 1) or x

    return _iterate(base, count)


def fallback(value: T | None, fallback_value: T) -> T:
    """
    Utility function that returns a value or a fallback if the value is None.

    Example:

    .. code-block:: python

        >>> fallback(5, 6)
        5
        >>> fallback(None, 6)
        6

    :param value:               Input value to evaluate. Can be None.
    :param fallback_value:      Value to return if the input value is None.

    :return:                    Input value or fallback value if input value is None.
    """
    return fallback_value if value is None else value
