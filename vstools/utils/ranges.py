from __future__ import annotations

import warnings
from typing import Iterable, overload
from itertools import chain, zip_longest

import vapoursynth as vs

from ..exceptions import CustomIndexError
from ..functions import check_ref_clip
from ..types import FrameRangeN, FrameRangesN, T, T0

__all__ = [
    'replace_ranges', 'rfs',

    'ranges_product',

    'interleave_arr'
]


def replace_ranges(
    clip_a: vs.VideoNode, clip_b: vs.VideoNode,
    ranges: FrameRangeN | FrameRangesN | None,
    exclusive: bool = False, use_plugin: bool = True,
    mismatch: bool = False
) -> vs.VideoNode:
    from ..functions import normalize_ranges

    if ranges != 0 and not ranges:
        return clip_a

    if not mismatch:
        check_ref_clip(clip_a, clip_b)

    if clip_a.num_frames != clip_b.num_frames:
        warnings.warn(
            f"replace_ranges: 'The number of frames ({clip_a.num_frames} vs. {clip_b.num_frames}) do not match! "
            "The function will still work, but you may run into unintended errors with the output clip!'"
        )

    nranges = normalize_ranges(clip_b, ranges)

    if use_plugin and hasattr(vs.core, 'remap'):
        return vs.core.remap.ReplaceFramesSimple(
            clip_a, clip_b, mismatch=mismatch,
            mappings=' '.join(f'[{s} {e + (exclusive if s != e else 0)}]' for s, e in nranges)
        )

    out = clip_a
    shift = 1 + exclusive

    for start, end in nranges:
        tmp = clip_b[start:end + shift]

        if start != 0:
            tmp = vs.core.std.Splice([out[: start], tmp], mismatch)

        if end < out.num_frames - 1:
            tmp = vs.core.std.Splice([tmp, out[end + shift:]], mismatch)

        out = tmp

    return out


# Aliases
rfs = replace_ranges


@overload
def ranges_product(range0: range | int, range1: range | int, /) -> Iterable[tuple[int, int]]:
    ...


@overload
def ranges_product(range0: range | int, range1: range | int, range2: range | int, /) -> Iterable[tuple[int, int, int]]:
    ...


def ranges_product(*_iterables: range | int) -> Iterable[tuple[int, ...]]:
    n_iterables = len(_iterables)

    if n_iterables <= 1:
        raise CustomIndexError(f'Not enough ranges passed! ({n_iterables})', ranges_product)

    iterables = [range(x) if isinstance(x, int) else x for x in _iterables]

    if n_iterables == 2:
        first_it, second_it = iterables

        for xx in first_it:
            for yy in second_it:
                yield xx, yy
    elif n_iterables == 3:
        first_it, second_it, third_it = iterables

        for xx in first_it:
            for yy in second_it:
                for zz in third_it:
                    yield xx, yy, zz
    else:
        raise CustomIndexError(f'Too many ranges passed! ({n_iterables})', ranges_product)


def interleave_arr(arr0: Iterable[T], arr1: Iterable[T0], n: int = 2) -> Iterable[T | T0]:
    if n == 1:
        return [x for x in chain(*zip_longest(arr0, arr1)) if x is not None]

    arr0_i, arr1_i = iter(arr0), iter(arr1)
    arr1_vals = arr0_vals = True

    while arr1_vals or arr0_vals:
        if arr0_vals:
            for _ in range(n):
                try:
                    yield next(arr0_i)
                except StopIteration:
                    arr0_vals = False

        if arr1_vals:
            try:
                yield next(arr1_i)
            except StopIteration:
                arr1_vals = False
