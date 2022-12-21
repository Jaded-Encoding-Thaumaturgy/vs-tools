from __future__ import annotations

from fractions import Fraction
from typing import Any, Iterable, Iterator, Sequence, overload

import vapoursynth as vs

from ..types import F, FrameRange, FrameRangeN, FrameRangesN, PlanesT, SupportsString, T, VideoNodeIterable

__all__ = [
    'normalize_seq',
    'normalize_planes',
    'to_arr',
    'flatten', 'flatten_vnodes',
    'normalize_franges',
    'normalize_ranges',
    'norm_func_name', 'norm_display_name'
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
    return list(val) if type(val) in {list, tuple, range, zip, set, map, enumerate} else [val]  # type: ignore


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
    if isinstance(items, (vs.RawNode, vs.RawFrame)):
        yield items
    else:
        for val in items:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                for sub_x in flatten(val):
                    yield sub_x
            else:
                yield val


def flatten_vnodes(clips: VideoNodeIterable) -> list[vs.VideoNode]:
    return list[vs.VideoNode](flatten(clips))  # type: ignore


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
        return func_name.strip()

    if not isinstance(func_name, type) and not callable(func_name):
        return str(func_name).strip()

    func = func_name

    if hasattr(func_name, '__name__'):
        func_name = func.__name__
    elif hasattr(func_name, '__qualname__'):
        func_name = func.__qualname__

    if callable(func):
        if hasattr(func, '__self__'):
            func_name = f'{func.__self__.__name__}.{func_name}'

    return str(func_name).strip()


def norm_display_name(obj: object) -> str:
    if isinstance(obj, Iterator):
        return ', '.join(norm_display_name(v) for v in obj).strip()

    if isinstance(obj, Fraction):
        return f'{obj.numerator}/{obj.denominator}'

    if isinstance(obj, dict):
        return '(' + ', '.join(f'{k}={v}' for k, v in obj.items()) + ')'

    return norm_func_name(obj)
