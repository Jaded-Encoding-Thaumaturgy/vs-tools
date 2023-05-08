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
    'normalize_list_to_ranges',
    'normalize_ranges_to_list',
    'normalize_franges',
    'normalize_ranges',
    'invert_ranges',
    'norm_func_name', 'norm_display_name'
]


@overload
def normalize_seq(val: Sequence[T], length: int = 3) -> list[T]:
    ...


@overload
def normalize_seq(val: T | Sequence[T], length: int = 3) -> list[T]:
    ...


def normalize_seq(val: T | Sequence[T], length: int = 3) -> list[T]:
    """
    Normalize a sequence of values.

    :param val:     Input value.
    :param length:  Amount of items in the output. Default: 3.
                    If original sequence length is less that this,
                    the last item will be repeated.

    :return:        List of normalized values with a set amount of items.
    """

    if not isinstance(val, Sequence):
        return [val] * length

    val = list(val) + [val[-1]] * (length - len(val))

    return val[:length]


def normalize_planes(clip: vs.VideoNode, planes: PlanesT = None) -> list[int]:
    """
    Normalize a sequence of planes.

    :param clip:        Input clip.
    :param planes:      Array of planes. If None, returns all planes of the input clip's format.
                        Default: None.
    :param pad:         Whether to pad the output list.
                        Default: False.

    :return:            Sorted list of planes.
    """

    assert clip.format

    if planes is None or planes == 4:
        planes = list(range(clip.format.num_planes))
    else:
        planes = to_arr(planes, sub=True)

    return list(sorted(set(planes).intersection(range(clip.format.num_planes))))


_iterables_t = (list, tuple, range, zip, set, map, enumerate)


@overload
def to_arr(val: list[T], *, sub: bool = False) -> list[T]:
    ...


@overload
def to_arr(val: T | Sequence[T], *, sub: bool = False) -> list[T]:
    ...


def to_arr(val: T | Sequence[T], *, sub: bool = False) -> list[T]:
    """Normalize any value into an iterable."""

    if sub:
        return list(val) if any(isinstance(val, x) for x in _iterables_t) else [val]  # type: ignore

    return list(val) if type(val) in _iterables_t else [val]  # type: ignore


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
    """Flatten an array of values."""

    if isinstance(items, (vs.RawNode, vs.RawFrame)):
        yield items
    else:
        for val in items:
            if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
                for sub_x in flatten(val):
                    yield sub_x
            else:
                yield val


def flatten_vnodes(
    *clips: VideoNodeIterable | tuple[VideoNodeIterable, ...], split_planes: bool = False
) -> list[vs.VideoNode]:
    """Flatten a single or multiple video nodes into their planes."""

    from .utils import split

    nodes = list[vs.VideoNode](flatten(clips))  # type: ignore

    if not split_planes:
        return nodes

    return sum(map(split, nodes), list[vs.VideoNode]())


def normalize_franges(franges: FrameRange, /) -> Iterable[int]:
    """
    Normalize frame ranges to an iterable of frame numbers.

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


def normalize_list_to_ranges(flist: Sequence[int], min_length: int = 0) -> list[tuple[int, int]]:
    flist2 = list[list[int]]()
    flist3 = list[int]()

    prev_n = -1

    for n in sorted(set(flist)):
        if prev_n + 1 != n:
            if flist3:
                flist2.append(flist3)
                flist3 = []
        flist3.append(n)
        prev_n = n

    if flist3:
        flist2.append(flist3)

    flist4 = [i for i in flist2 if len(i) > min_length]

    return list(zip(
        [i[0] for i in flist4],
        [i[-1] for j, i in enumerate(flist4)]
    ))


def normalize_ranges_to_list(franges: Iterable[FrameRange]) -> list[int]:
    out = list[int]()

    for frange in franges:
        out.extend(normalize_franges(frange))

    return out


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
        >>> normalize_ranges(clip, [(24, 100), (80, 150)])
        [(24, 150)]


    :param clip:        Input clip.
    :param franges:     Frame range or list of frame ranges.

    :return:            List of positive frame ranges.
    """

    ranges = ranges if isinstance(ranges, list) else [ranges]  # type:ignore

    out = []

    for r in ranges:
        if r is None:
            r = (None, None)

        if isinstance(r, tuple):
            start, end = r
            if start is None:
                start = 0
            if end is None:
                end = clip.num_frames - 1
        else:
            start = r
            end = r

        if start < 0:
            start = clip.num_frames - 1 + start

        if end < 0:
            end = clip.num_frames - 1 + end

        out.append((start, end))

    return normalize_list_to_ranges([
        x for start, end in out for x in range(start, end + 1)
    ])


def invert_ranges(
        clipa: vs.VideoNode, clipb: vs.VideoNode | None, ranges: FrameRangeN | FrameRangesN) -> list[
        tuple[int, int]]:
    norm_ranges = normalize_ranges(clipb or clipa, ranges)

    b_frames = set(normalize_ranges_to_list(norm_ranges))

    return normalize_list_to_ranges([
        i for i in range(0, clipa.num_frames + 1)
        if i not in b_frames
    ])


def norm_func_name(func_name: SupportsString | F) -> str:
    """Normalize a class, function, or other object to obtain its name"""

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
    """Get a fancy name from any object."""

    if isinstance(obj, Iterator):
        return ', '.join(norm_display_name(v) for v in obj).strip()

    if isinstance(obj, Fraction):
        return f'{obj.numerator}/{obj.denominator}'

    if isinstance(obj, dict):
        return '(' + ', '.join(f'{k}={v}' for k, v in obj.items()) + ')'

    return norm_func_name(obj)
