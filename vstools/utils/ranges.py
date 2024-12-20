from __future__ import annotations

import re
import warnings
from typing import Callable, Sequence, Union, overload

import vapoursynth as vs
from stgpytools import CustomValueError, flatten, interleave_arr, ranges_product

from ..exceptions import FormatsMismatchError, FramerateMismatchError, LengthMismatchError, ResolutionsMismatchError
from ..functions import check_ref_clip
from ..types import FrameRangeN, FrameRangesN

__all__ = [
    'replace_ranges',

    'remap_frames',

    'replace_every',

    'ranges_product',

    'interleave_arr',

    'convert_rfs',
]


_gc_func_gigacope = []

RangesCallback = Union[
    Callable[[int], bool],
    Callable[[vs.VideoFrame], bool],
    Callable[[list[vs.VideoFrame]], bool],
    Callable[[vs.VideoFrame | list[vs.VideoFrame]], bool],
    Callable[[int, vs.VideoFrame], bool],
    Callable[[int, list[vs.VideoFrame]], bool],
    Callable[[int, vs.VideoFrame | list[vs.VideoFrame]], bool]
]


@overload
def replace_ranges(
    clip_a: vs.VideoNode, clip_b: vs.VideoNode,
    ranges: FrameRangeN | FrameRangesN | Callable[[vs.VideoFrame], bool] | Callable[[int, vs.VideoFrame], bool] | None,
    exclusive: bool = False, mismatch: bool = False,
    *, prop_src: vs.VideoNode
) -> vs.VideoNode:
    ...


@overload
def replace_ranges(
    clip_a: vs.VideoNode, clip_b: vs.VideoNode, ranges: FrameRangeN | FrameRangesN | Callable[
        [list[vs.VideoFrame]], bool
    ] | Callable[[int, list[vs.VideoFrame]], bool] | None, exclusive: bool = False,
    mismatch: bool = False,
    *, prop_src: list[vs.VideoNode]
) -> vs.VideoNode:
    ...


@overload
def replace_ranges(
    clip_a: vs.VideoNode, clip_b: vs.VideoNode, ranges: FrameRangeN | FrameRangesN | Callable[
        [vs.VideoFrame | list[vs.VideoFrame]], bool
    ] | Callable[[int, vs.VideoFrame | list[vs.VideoFrame]], bool] | None, exclusive: bool = False,
    mismatch: bool = False, *, prop_src: vs.VideoNode | list[vs.VideoNode] | None = None
) -> vs.VideoNode:
    ...


@overload
def replace_ranges(
    clip_a: vs.VideoNode, clip_b: vs.VideoNode,
    ranges: FrameRangeN | FrameRangesN | Callable[[int], bool] | None,
    exclusive: bool = False, mismatch: bool = False, *, prop_src: None = None
) -> vs.VideoNode:
    ...


@overload
def replace_ranges(
    clip_a: vs.VideoNode, clip_b: vs.VideoNode,
    ranges: FrameRangeN | FrameRangesN | RangesCallback | None,
    exclusive: bool = False, mismatch: bool = False,
    *, prop_src: vs.VideoNode | list[vs.VideoNode] | None = None
) -> vs.VideoNode:
    ...


def replace_ranges(
    clip_a: vs.VideoNode, clip_b: vs.VideoNode,
    ranges: FrameRangeN | FrameRangesN | RangesCallback | None,
    exclusive: bool = False, mismatch: bool = False,
    *, prop_src: vs.VideoNode | list[vs.VideoNode] | None = None
) -> vs.VideoNode:
    """
    Replaces frames in a clip, either with pre-calculated indices or on-the-fly with a callback.
    Frame ranges are inclusive. This behaviour can be changed by setting `exclusive=True`.

    Examples with clips ``black`` and ``white`` of equal length:
        * ``replace_ranges(black, white, [(0, 1)])``: replace frames 0 and 1 with ``white``
        * ``replace_ranges(black, white, [(None, None)])``: replace the entire clip with ``white``
        * ``replace_ranges(black, white, [(0, None)])``: same as previous
        * ``replace_ranges(black, white, [(200, None)])``: replace 200 until the end with ``white``
        * ``replace_ranges(black, white, [(200, -1)])``: replace 200 until the end with ``white``,
                                                         leaving 1 frame of ``black``

    Optional Dependencies:
        * Either of the following two plugins:
            * `VS Julek Plugin <https://github.com/dnjulek/vapoursynth-julek-plugin>`_ (recommended!)
            * `VSRemapFrames <https://github.com/Irrational-Encoding-Wizardry/Vapoursynth-RemapFrames>`_

    :param clip_a:      Original clip.
    :param clip_b:      Replacement clip.
    :param ranges:      Ranges to replace clip_a (original clip) with clip_b (replacement clip).
                        Integer values in the list indicate single frames,
                        Tuple values indicate inclusive ranges.
                        Callbacks must return true to replace a with b.
                        Negative integer values will be wrapped around based on clip_b's length.
                        None values are context dependent:
                            * None provided as sole value to ranges: no-op
                            * Single None value in list: Last frame in clip_b
                            * None as first value of tuple: 0
                            * None as second value of tuple: Last frame in clip_b
    :param exclusive:   Use exclusive ranges (Default: False).
    :param mismatch:    Accept format or resolution mismatch between clips.

    :return:            Clip with ranges from clip_a replaced with clip_b.
    """

    from ..functions import invert_ranges, normalize_ranges, normalize_ranges_to_list

    if ranges != 0 and not ranges or clip_a is clip_b:
        return clip_a

    if not mismatch:
        check_ref_clip(clip_a, clip_b)

    if callable(ranges):
        from inspect import Signature

        signature = Signature.from_callable(ranges, eval_str=True)

        params = set(signature.parameters.keys())

        base_clip = clip_a.std.BlankClip(
            keep=True, varformat=(clip_a.format != clip_b.format),
            varsize=(clip_a.width, clip_a.height) != (clip_b.width, clip_b.height)
        )

        callback: RangesCallback = ranges

        if 'f' in params and not prop_src:
            raise CustomValueError(
                'For passing f to the callback you must specify the node(s) to grab the frame from via prop_src.'
            )

        if 'f' in params and 'n' in params:
            def _func(n: int, f: vs.VideoFrame) -> vs.VideoNode:
                return clip_b if callback(n, f) else clip_a  # type: ignore
        elif 'f' in params:
            def _func(n: int, f: vs.VideoFrame) -> vs.VideoNode:
                return clip_b if callback(f) else clip_a  # type: ignore
        elif 'n' in params:
            def _func(n: int) -> vs.VideoNode:  # type: ignore
                return clip_b if callback(n) else clip_a  # type: ignore
        else:
            raise CustomValueError('Callback must have signature ((n, f) | (n) | (f)) -> bool!')

        _func.__callback = callback  # type: ignore
        _gc_func_gigacope.append(_func)

        return base_clip.std.FrameEval(_func, prop_src if 'f' in params else None, [clip_a, clip_b])

    b_ranges = normalize_ranges(clip_b, ranges)
    do_splice_trim = len(b_ranges) <= 15
    min_frame_num = min(clip_a.num_frames, clip_b.num_frames)

    if not do_splice_trim and any(e >= min_frame_num for _, e in b_ranges):
        raise CustomValueError(
            f'You cannot replace frames that are out of bounds ({min_frame_num=})!',
            replace_ranges, [r for r in b_ranges if r[1] >= min_frame_num]
        )

    if clip_a.num_frames != clip_b.num_frames:
        warnings.warn(
            f"replace_ranges: 'The number of frames of the clips don't match! "
            f"({clip_a.num_frames=}, {clip_b.num_frames=})\n"
            "The function will still work, but you may run into undefined behavior, or a broken output clip!'"
        )

    if not do_splice_trim:
        if clip_a.num_frames != clip_b.num_frames:
            diff = abs(clip_a.num_frames - clip_b.num_frames)

            if clip_a.num_frames < clip_b.num_frames:
                clip_a = clip_a + clip_a[-1] * diff
            else:
                clip_b = clip_b + clip_b[-1] * diff

        try:
            if hasattr(vs.core, 'julek'):
                return vs.core.julek.RFS(
                    clip_a, clip_b, [y for (s, e) in b_ranges for y in range(s, e + (not exclusive if s != e else 1))],
                    mismatch=mismatch
                )
            elif hasattr(vs.core, 'remap'):
                return vs.core.remap.ReplaceFramesSimple(
                    clip_a, clip_b, mismatch=mismatch,
                    mappings=' '.join(f'[{s} {e + (exclusive if s != e else 0)}]' for s, e in b_ranges)
                )
        except vs.Error as e:
            msg = str(e).replace('vapoursynth.Error: ReplaceFramesSimple: ', '')

            match msg:
                case "Clip lengths don't match":
                    raise LengthMismatchError(replace_ranges, (clip_a, clip_b))
                case "Clip dimensions don't match":
                    raise ResolutionsMismatchError(replace_ranges, (clip_a, clip_b))
                case "Clip formats don't match":
                    raise FormatsMismatchError(replace_ranges, (clip_a, clip_b))
                case "Clip frame rates don't match":
                    raise FramerateMismatchError(replace_ranges, (clip_a, clip_b))
                case _:
                    raise CustomValueError(msg, replace_ranges)

    if do_splice_trim:
        shift = 1 - exclusive

        a_ranges = invert_ranges(clip_b, clip_a, b_ranges)

        a_trims = [clip_a[max(0, start - exclusive):end + shift + exclusive] for start, end in a_ranges]
        b_trims = [clip_b[start:end + shift] for start, end in b_ranges]

        if a_ranges:
            main, other = (a_trims, b_trims) if (a_ranges[0][0] == 0) else (b_trims, a_trims)
        else:
            main, other = (b_trims, a_trims) if (b_ranges[0][0] == 0) else (a_trims, b_trims)

        return vs.core.std.Splice(list(interleave_arr(main, other, 1)), mismatch)

    b_frames = set(normalize_ranges_to_list(b_ranges))
    return replace_ranges(clip_a, clip_b, lambda n: n in b_frames)


def remap_frames(clip: vs.VideoNode, ranges: Sequence[int | tuple[int, int]]) -> vs.VideoNode:
    frame_map = list(flatten(  # type: ignore
        f if isinstance(f, int) else range(f[0], f[1] + 1) for f in ranges
    ))

    base = clip.std.BlankClip(length=len(frame_map))

    return base.std.FrameEval(lambda n: clip[frame_map[n]], None, clip)


def replace_every(
    clipa: vs.VideoNode, clipb: vs.VideoNode, cycle: int, offsets: Sequence[int], modify_duration: bool = True
) -> vs.VideoNode:
    offsets_a = [x * 2 for x in range(cycle) if x not in offsets]
    offsets_b = [x * 2 + 1 for x in offsets]
    offsets = sorted(offsets_a + offsets_b)

    interleaved = vs.core.std.Interleave([clipa, clipb])

    return interleaved.std.SelectEvery(cycle * 2, offsets, modify_duration)


def convert_rfs(rfs_string: str) -> FrameRangesN:
    """
    Convert `ReplaceFramesSimple`-styled ranges to `replace_ranges`-styled ranges.

    This function accepts RFS ranges as a string, consistent with RFS handling.
    The input string is validated before processing.

    Supports both '[x y]' and 'x' frame numbering styles.
    Returns an empty list if no valid frames are found.

    :param rfs_string:          A string representing frame ranges in ReplaceFramesSimple format.

    :return:                    A FrameRangesN list containing frame ranges compatible with `replace_ranges`.
                                Returns an empty list if no valid frames are found.

    :raises CustomValueError:   If the input string contains invalid characters.
    """

    rfs_string = str(rfs_string).strip()

    if not rfs_string:
        return []

    valid_chars = set('0123456789[] ')
    illegal_chars = set(rfs_string) - valid_chars

    if illegal_chars:
        reason = ', '.join(f"{c}:{rfs_string.index(c)}" for c in sorted(illegal_chars, key=rfs_string.index))

        raise CustomValueError('Invalid characters found in input string!', convert_rfs, reason)

    return [
        int(match[2]) if match[2] else (int(match[0]), int(match[1]))
        for match in re.findall(r'\[(\d+)\s+(\d+)\]|(\d+)', rfs_string)
    ]
