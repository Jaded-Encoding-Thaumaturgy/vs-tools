from __future__ import annotations

from typing import Any, Iterable, Sequence, overload

import vapoursynth as vs

from ..types import AnythingElse, F, FrameRange, FrameRangeN, FrameRangesN, PlanesT, SupportsString, T

__all__ = [
    'normalize_seq',
    'normalize_planes',
    'to_arr',
    'flatten',
    'arr_to_len',
    'normalize_franges',
    'normalize_ranges',
    'norm_func_name'
]


@overload
def normalize_seq(val: Sequence[AnythingElse], length_max: int = 3) -> list[AnythingElse]:
    ...


@overload
def normalize_seq(val: AnythingElse, length_max: int = 3) -> list[AnythingElse]:
    ...


def normalize_seq(val: Any, length_max: int = 3) -> Any:
    """
    Normalize a sequence of values.

    :param val:         Input value.
    :param length_max:  Maximum amount of items allowed in the output.
                        Default: 3.

    :return:            List of normalized values with a set amount of items.
    """
    if not isinstance(val, Sequence):
        return [val] * length_max

    val = list(val) + [val[-1]] * (length_max - len(val))

    return val[:length_max]


def normalize_planes(clip: vs.VideoNode, planes: PlanesT = None, pad: bool = False) -> list[int]:
    """
    Normalize a sequence of planes.

    :param clip:        Input clip.
    :param planes:      Array of planes. If None, returns the maximum amount of planes in the input clip.
                        Default: None.
    :param pad:         Whether to pad the output list.
                        Default: False.

    :return:            Sorted list of planes.
    """
    assert clip.format

    if planes is None:
        planes = list(range(clip.format.num_planes))
    else:
        planes = to_arr(planes)

    if pad:
        return normalize_seq(planes, clip.format.num_planes)

    return list(set(sorted(planes)))


@overload
def to_arr(val: Sequence[AnythingElse]) -> list[AnythingElse]:
    ...


@overload
def to_arr(val: AnythingElse) -> list[AnythingElse]:
    ...


def to_arr(val: Any) -> Any:
    """Convert value into an array."""
    return val if type(val) in {list, tuple, range, zip, set, map, enumerate} else [val]


@overload
def flatten(items: Iterable[Iterable[AnythingElse]]) -> Iterable[AnythingElse]:
    ...


@overload
def flatten(items: Iterable[AnythingElse]) -> Iterable[AnythingElse]:
    ...


def flatten(items: Any) -> Any:
    """Flatten an array of values."""
    for val in items:
        if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
            for sub_x in flatten(val):
                yield sub_x
        else:
            yield val


def arr_to_len(array: Sequence[T], length: int = 3) -> list[T]:
    """Limit the length of an array by *n* items."""
    return (list(array) + [array[-1]] * length)[:length]


def normalize_franges(franges: FrameRange, /) -> Iterable[int]:
    """
    Normalize frame ranges to a valid iterable of ranges.

    @@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS
    Not sure if this is the right way to describe it ^

    :param franges:     Frame range or list of frame ranges.

    :return:            List of positive frame ranges.
    """
    if isinstance(franges, int):
        return [franges]

    if isinstance(franges, tuple):
        start, stop = franges
        step = -1 if stop < start else 1

        return range(start, stop + step, step)

    return franges


def normalize_ranges(clip: vs.VideoNode, ranges: FrameRangeN | FrameRangesN) -> list[tuple[int, int]]:
    """
    Normalize ranges to a list of positive ranges.

    Frame ranges can include None and negative values.
    None will be converted to either 0 if it's the first value in a FrameRange,
    or the clip's length if it's the second item.
    Negative values will be subtracted from the clip's length.

    Examples:

    .. code-block:: python

        >>> clip.num_frames
        1000
        >>> normalize_ranges(clip, (None, None))
        [(0, 1000)]
        >>> normalize_ranges(clip, (24, -24))
        [(24, 976)]


    :param clip:        Input clip.
    :param franges:     Frame range or list of frame ranges.

    :return:            List of positive frame ranges.
    """
    ranges = ranges if isinstance(ranges, list) else [ranges]

    out = []

    for r in ranges:
        if isinstance(r, tuple):
            start, end = r
            if start is None:
                start = 0
            if end is None:
                end = clip.num_frames - 1
        elif r is None:
            start = clip.num_frames - 1
            end = clip.num_frames - 1
        else:
            start = r
            end = r

        if start < 0:
            start = clip.num_frames - 1 + start

        if end < 0:
            end = clip.num_frames - 1 + end

        out.append((start, end))

    return out


def norm_func_name(func_name: SupportsString | F) -> str:
    """Normalize a function's name."""
    if callable(func_name):
        func = func_name

        func_name = f'{func.__name__}'

        if hasattr(func, '__self__'):
            func_name = f'{func.__self__.__name__}.{func_name}'  # type: ignore

    return str(func_name)
