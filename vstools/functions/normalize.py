from __future__ import annotations

from typing import Any, Iterable, Sequence, overload

import vapoursynth as vs
from stgpytools import T, norm_display_name, norm_func_name, normalize_list_to_ranges, normalize_ranges_to_list, to_arr
from stgpytools import (
    flatten as stg_flatten,
    invert_ranges as stg_invert_ranges,
    normalize_range as normalize_franges,
    normalize_ranges as stg_normalize_ranges,
    normalize_seq as stg_normalize_seq
)

from ..types import FrameRangeN, FrameRangesN, PlanesT, VideoNodeIterable

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
    return stg_normalize_seq(val, length)


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
    """Flatten an array of values, clips and frames included."""

    if isinstance(items, (vs.RawNode, vs.RawFrame)):
        yield items
    else:
        yield from stg_flatten(items)


def flatten_vnodes(
    *clips: VideoNodeIterable | tuple[VideoNodeIterable, ...], split_planes: bool = False
) -> list[vs.VideoNode]:
    """Flatten a single or multiple video nodes into their planes."""

    from .utils import split

    nodes = list[vs.VideoNode](flatten(clips))  # type: ignore

    if not split_planes:
        return nodes

    return sum(map(split, nodes), list[vs.VideoNode]())


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
        [(0, 999)]
        >>> normalize_ranges(clip, (24, -24))
        [(24, 975)]
        >>> normalize_ranges(clip, [(24, 100), (80, 150)])
        [(24, 150)]


    :param clip:        Input clip.
    :param franges:     Frame range or list of frame ranges.

    :return:            List of positive frame ranges.
    """

    return stg_normalize_ranges(ranges, clip.num_frames)


def invert_ranges(
    clipa: vs.VideoNode, clipb: vs.VideoNode | None, ranges: FrameRangeN | FrameRangesN
) -> list[tuple[int, int]]:
    return stg_invert_ranges(ranges, clipa.num_frames, None if clipb is None else clipb.num_frames)
