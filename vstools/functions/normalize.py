from __future__ import annotations

from typing import Any, Iterable, Sequence, overload

import vapoursynth as vs

from ..types import F, FrameRange, FrameRangeN, FrameRangesN, PlanesT, SupportsString, T

__all__ = [
    'normalize_seq',
    'normalize_planes',
    'to_arr',
    'flatten',
    'normalize_franges',
    'normalize_ranges',
    'norm_func_name'
]


def normalize_seq(val: T | Sequence[T], length_max: int = 3) -> list[T]:
    if not isinstance(val, Sequence):
        return [val] * length_max

    val = list(val) + [val[-1]] * (length_max - len(val))

    return val[:length_max]


def normalize_planes(clip: vs.VideoNode, planes: PlanesT = None, pad: bool = False) -> list[int]:
    assert clip.format

    if planes is None:
        planes = list(range(clip.format.num_planes))
    else:
        planes = to_arr(planes)

    if pad:
        return normalize_seq(planes, clip.format.num_planes)

    return list(set(sorted(planes)))


def to_arr(val: T | Sequence[T]) -> list[T]:
    return val if type(val) in {list, tuple, range, zip, set, map, enumerate} else [val]  # type: ignore


@overload
def flatten(items: T | Iterable[T | Iterable[T | Iterable[T]]]) -> Iterable[T]:
    ...


@overload
def flatten(items: T | Iterable[T | Iterable[T]]) -> Iterable[T]:  # type: ignore
    ...


@overload
def flatten(items: T | Iterable[T]) -> Iterable[T]:  # type: ignore
    ...


def flatten(items: Any) -> Any:
    for val in items:
        if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
            for sub_x in flatten(val):
                yield sub_x
        else:
            yield val


def normalize_franges(franges: FrameRange, /) -> Iterable[int]:
    if isinstance(franges, int):
        return [franges]

    if isinstance(franges, tuple):
        start, stop = franges
        step = -1 if stop < start else 1

        return range(start, stop + step, step)

    return franges


def normalize_ranges(clip: vs.VideoNode, ranges: FrameRangeN | FrameRangesN) -> list[tuple[int, int]]:
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
    if isinstance(func_name, str):
        return func_name

    if not isinstance(func_name, type) and not callable(func_name):
        return str(func_name)

    func = func_name

    if hasattr(func_name, '__name__'):
        func_name = func.__name__
    elif hasattr(func_name, '__qualname__'):
        func_name = func.__qualname__

    if callable(func):
        if hasattr(func, '__self__'):
            func_name = f'{func.__self__.__name__}.{func_name}'  # type: ignore

    return str(func_name)
