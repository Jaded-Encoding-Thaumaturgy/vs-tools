from __future__ import annotations

import warnings
from itertools import chain, zip_longest
from typing import Iterable, overload

import vapoursynth as vs

from ..exceptions import (
    CustomIndexError, CustomValueError, FormatsMismatchError, FramerateMismatchError, LengthMismatchError,
    ResolutionsMismatchError
)
from ..functions import check_ref_clip
from ..types import T0, FrameRangeN, FrameRangesN, T

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
    """
    Remaps frame indices in a clip using ints and tuples rather than a string.

    Frame ranges are inclusive. This behaviour can be changed by setting `exclusive=True`.

    If you're trying to splice in clips, it's recommended you use :py:func:`insert_clip` instead.

    This function will try to call the `VapourSynth-RemapFrames` plugin before doing any of its own processing.
    This should come with a speed boost, so it's recommended you install it.

    Examples with clips ``black`` and ``white`` of equal length:
        * ``replace_ranges(black, white, [(0, 1)])``: replace frames 0 and 1 with ``white``
        * ``replace_ranges(black, white, [(None, None)])``: replace the entire clip with ``white``
        * ``replace_ranges(black, white, [(0, None)])``: same as previous
        * ``replace_ranges(black, white, [(200, None)])``: replace 200 until the end with ``white``
        * ``replace_ranges(black, white, [(200, -1)])``: replace 200 until the end with ``white``,
                                                         leaving 1 frame of ``black``

    Alias for this function is ``rfs``.

    Optional Dependencies:
        * `use_plugin=True`: `VSRemapFrames <https://github.com/Irrational-Encoding-Wizardry/Vapoursynth-RemapFrames>`_

    :param clip_a:      Original clip.
    :param clip_b:      Replacement clip.
    :param ranges:      Ranges to replace clip_a (original clip) with clip_b (replacement clip).
                        Integer values in the list indicate single frames,
                        Tuple values indicate inclusive ranges.
                        Negative integer values will be wrapped around based on clip_b's length.
                        None values are context dependent:
                            * None provided as sole value to ranges: no-op
                            * Single None value in list: Last frame in clip_b
                            * None as first value of tuple: 0
                            * None as second value of tuple: Last frame in clip_b
    :param exclusive:   Use exclusive ranges (Default: False).
    :param use_plugin:  Use the ReplaceFramesSimple plugin for the rfs call (Default: True).
    :param mismatch:    Accept format or resolution mismatch between clips.

    :return:            Clip with ranges from clip_a replaced with clip_b.
    """

    from ..functions import normalize_ranges

    if ranges != 0 and not ranges:
        return clip_a

    if not mismatch:
        check_ref_clip(clip_a, clip_b)

    nranges = normalize_ranges(clip_b, ranges)

    if use_plugin and hasattr(vs.core, 'remap'):
        try:
            return vs.core.remap.ReplaceFramesSimple(  # type: ignore
                clip_a, clip_b, mismatch=mismatch,
                mappings=' '.join(f'[{s} {e + (exclusive if s != e else 0)}]' for s, e in nranges)
            )
        except vs.Error as e:
            msg = str(e).replace('vapoursynth.Error: ReplaceFramesSimple: ', '')

            match msg:
                case "Clip lengths don't match":
                    raise LengthMismatchError(replace_ranges, [clip_a, clip_b])
                case "Clip dimensions don't match":
                    raise ResolutionsMismatchError(replace_ranges, [clip_a, clip_b])
                case "Clip formats don't match":
                    raise FormatsMismatchError(replace_ranges, [clip_a, clip_b])
                case "Clip frame rates don't match":
                    raise FramerateMismatchError(replace_ranges, [clip_a, clip_b])
                case _:
                    raise CustomValueError(msg, replace_ranges)

    if clip_a.num_frames != clip_b.num_frames:
        warnings.warn(
            f"replace_ranges: 'The number of frames of the clips don't match! "
            f"({clip_a.num_frames=}, {clip_b.num_frames=})\n"
            "The function will still work, but you may run into undefined behavior, or a broken output clip!'"
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
    """
    Take two or three lenghts/ranges and make a cartesian product of them.

    Useful for getting all coordinates of a frame.
    For example ranges_product(1920, 1080) will give you [(0, 0), (0, 1), (0, 2), ..., (1919, 1078), (1919, 1079)].
    """

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
    """
    Interleave two arrays of variable length.

    :param arr0:    First array to be interleaved.
    :param arr1:    Second array to be interleaved.
    :param n:       The number of elements from arr0 to include in the interleaved sequence
                    before including an element from arr1.

    :yield:         Elements from either arr0 or arr01.
    """
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
