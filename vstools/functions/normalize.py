from __future__ import annotations

from typing import Any, Iterable, Sequence, overload

import vapoursynth as vs

from ..types import AnythingElse, F, FrameRange, FrameRangeN, FrameRangesN, PlanesT, SupportsString, T


@overload
def normalise_seq(val: Sequence[AnythingElse], length_max: int = 3) -> list[AnythingElse]:
    pass


@overload
def normalise_seq(val: AnythingElse, length_max: int = 3) -> list[AnythingElse]:
    pass


def normalise_seq(val: Any, length_max: int = 3) -> Any:
    if not isinstance(val, Sequence):
        return [val] * length_max

    val = list(val) + [val[-1]] * (length_max - len(val))

    return val[:length_max]


def normalise_planes(clip: vs.VideoNode, planes: PlanesT = None, pad: bool = False) -> list[int]:
    assert clip.format

    if planes is None:
        planes = list(range(clip.format.num_planes))
    else:
        planes = to_arr(planes)

    if pad:
        return normalise_seq(planes, clip.format.num_planes)

    return list(set(sorted(planes)))


@overload
def to_arr(val: Sequence[AnythingElse]) -> list[AnythingElse]:
    pass


@overload
def to_arr(val: AnythingElse) -> list[AnythingElse]:
    pass


def to_arr(val: Any) -> Any:
    return val if type(val) in {list, tuple, range, zip, set, map, enumerate} else [val]


@overload
def flatten(items: Iterable[Iterable[AnythingElse]]) -> Iterable[AnythingElse]:
    ...


@overload
def flatten(items: Iterable[AnythingElse]) -> Iterable[AnythingElse]:
    ...


def flatten(items: Any) -> Any:
    for val in items:
        if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
            for sub_x in flatten(val):
                yield sub_x
        else:
            yield val


def arr_to_len(array: Sequence[T], length: int = 3) -> list[T]:
    return (list(array) + [array[-1]] * length)[:length]


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
    if callable(func_name):
        func = func_name

        func_name = f'{func.__name__}: '

        if hasattr(func, '__self__'):
            func_name = f'{func.__self__.__name__}.{func_name}'  # type: ignore

    return str(func_name)
