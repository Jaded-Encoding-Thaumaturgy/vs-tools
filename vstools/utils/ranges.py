from __future__ import annotations

import warnings

import vapoursynth as vs

from ..types import FrameRangeN, FrameRangesN

__all__ = [
    'replace_ranges', 'rfs'
]


def replace_ranges(
    clip_a: vs.VideoNode, clip_b: vs.VideoNode,
    ranges: FrameRangeN | FrameRangesN | None,
    exclusive: bool = False, use_plugin: bool = True
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
        * `use_plugin=True`:
        `VapourSynth-RemapFrames <https://github.com/Irrational-Encoding-Wizardry/Vapoursynth-RemapFrames>`_

    :param clip_a:          Original clip.
    :param clip_b:          Replacement clip.
    :param ranges:          Ranges to replace clip_a (original clip) with clip_b (replacement clip).
                            Integer values in the list indicate single frames,
                            Tuple values indicate inclusive ranges.
                            Negative integer values will be wrapped around based on clip_b's length.
                            None values are context dependent:
                                * None provided as sole value to ranges: no-op
                                * Single None value in list: Last frame in clip_b
                                * None as first value of tuple: 0
                                * None as second value of tuple: Last frame in clip_b
    :param exclusive:       Use exclusive ranges (Default: False).
    :param use_plugin:      Use the ReplaceFramesSimple plugin for the rfs call (Default: True).

    :return:                Clip with ranges from clip_a replaced with clip_b.
    """
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
