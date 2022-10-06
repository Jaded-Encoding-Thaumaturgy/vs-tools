from __future__ import annotations
from typing import Iterable, overload

import warnings

import vapoursynth as vs

from ..types import FrameRangeN, FrameRangesN
from ..exceptions import CustomIndexError

__all__ = [
    'replace_ranges', 'rfs',

    'ranges_product'
]


def replace_ranges(
    clip_a: vs.VideoNode, clip_b: vs.VideoNode,
    ranges: FrameRangeN | FrameRangesN | None,
    exclusive: bool = False, use_plugin: bool = True
) -> vs.VideoNode:
    from ..functions import normalize_ranges

    if ranges != 0 and not ranges:
        return clip_a

    if clip_a.num_frames != clip_b.num_frames:
        warnings.warn(
            f"replace_ranges: 'The number of frames ({clip_a.num_frames} vs. {clip_b.num_frames}) do not match! "
            "The function will still work, but you may run into unintended errors with the output clip!'"
        )

    nranges = normalize_ranges(clip_b, ranges)

    if use_plugin and hasattr(vs.core, 'remap'):
        return vs.core.remap.ReplaceFramesSimple(
            clip_a, clip_b, mismatch=True,
            mappings=' '.join(f'[{s} {e + (exclusive if s != e else 0)}]' for s, e in nranges)
        )

    out = clip_a
    shift = 1 + exclusive

    for start, end in nranges:
        tmp = clip_b[start:end + shift]
        if start != 0:
            tmp = out[: start] + tmp
        if end < out.num_frames - 1:
            tmp = tmp + out[end + shift:]
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
