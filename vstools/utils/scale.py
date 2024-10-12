from __future__ import annotations

from typing import Sequence

import vapoursynth as vs
from stgpytools import normalize_seq

from ..enums import ColorRange, ColorRangeT
from ..types import HoldsVideoFormatT, VideoFormatT
from .info import get_depth, get_video_format

__all__ = [
    'scale_value',

    'get_lowest_value', 'get_neutral_value', 'get_peak_value',
    'get_lowest_values', 'get_neutral_values', 'get_peak_values',
]


def scale_value(
    value: int | float,
    input_depth: int | VideoFormatT | HoldsVideoFormatT,
    output_depth: int | VideoFormatT | HoldsVideoFormatT,
    range_in: ColorRangeT | None = None,
    range_out: ColorRangeT | None = None,
    scale_offsets: bool = True,
    chroma: bool = False,
    family: vs.ColorFamily | None = None
) -> int | float:
    """
    Converts the value to the specified bit depth, or bit depth of the clip/format specified.

    :param value:           Value to scale.
    :param input_depth:     Input bit depth, or clip, frame, format from where to get it.
    :param output_depth:    Output bit depth, or clip, frame, format from where to get it.
    :param range_in:        Color range of the input value
    :param range_out:       Color range of the desired output.
    :param scale_offsets:   Whether or not to apply & map YUV zero-point offsets.
                            Set to True when converting absolute color values.
                            Set to False when converting color deltas.
                            Only relevant if integer formats are involved.
    :param chroma:          Whether or not to treat values as chroma values instead of luma.
    :param family:          Which color family to assume for calculations.

    :return:                Scaled value.
    """

    out_value = float(value)

    in_fmt = get_video_format(input_depth)
    out_fmt = get_video_format(output_depth)

    if range_in is None:
        if isinstance(input_depth, vs.VideoNode):
            range_in = ColorRange(input_depth)
        elif vs.RGB in (in_fmt.color_family, family):
            range_in = ColorRange.FULL
        else:
            range_in = ColorRange.LIMITED

    if range_out is None:
        if isinstance(output_depth, vs.VideoNode):
            range_out = ColorRange(output_depth)
        elif vs.RGB in (out_fmt.color_family, family):
            range_out = ColorRange.FULL
        else:
            range_out = ColorRange.LIMITED

    if input_depth == output_depth and range_in == range_out and in_fmt.sample_type == out_fmt.sample_type:
        return out_value

    if vs.RGB in (in_fmt.color_family, out_fmt.color_family, family):
        chroma = False

    input_peak = get_peak_value(in_fmt, chroma, range_in, family)
    input_lowest = get_lowest_value(in_fmt, chroma, range_in, family)
    output_peak = get_peak_value(out_fmt, chroma, range_out, family)
    output_lowest = get_lowest_value(out_fmt, chroma, range_out, family)

    if scale_offsets and in_fmt.sample_type is vs.INTEGER:
        if chroma:
            out_value -= 128 << (in_fmt.bits_per_sample - 8)
        elif range_in.is_limited:
            out_value -= 16 << (in_fmt.bits_per_sample - 8)

    out_value *= (output_peak - output_lowest) / (input_peak - input_lowest)

    if scale_offsets and out_fmt.sample_type is vs.INTEGER:
        if chroma:
            out_value += 128 << (out_fmt.bits_per_sample - 8)
        elif range_out.is_limited:
            out_value += 16 << (out_fmt.bits_per_sample - 8)

    if out_fmt.sample_type is vs.INTEGER:
        out_value = max(min(round(out_value), get_peak_value(out_fmt, range_in=ColorRange.FULL)), 0)

    return out_value


def get_lowest_value(
    clip_or_depth: int | VideoFormatT | HoldsVideoFormatT, chroma: bool = False,
    range_in: ColorRangeT | None = None, family: vs.ColorFamily | None = None
) -> float:
    """
    Returns the lowest value for the specified bit depth, or bit depth of the clip/format specified.

    :param clip_or_depth:   Input bit depth, or clip, frame, format from where to get it.
    :param chroma:          Whether to get luma (default) or chroma plane value.
    :param range_in:        Whether to get limited or full range lowest value.
    :param family:          Which color family to assume for calculations.

    :return:                Lowest possible value.
    """

    fmt = get_video_format(clip_or_depth)

    if fmt.sample_type is vs.FLOAT:
        return -0.5 if chroma else 0.0

    if (is_rgb := vs.RGB in (fmt.color_family, family)):
        chroma = False

    if range_in is None:
        if isinstance(clip_or_depth, vs.VideoNode):
            range_in = ColorRange(clip_or_depth)
        elif is_rgb:
            range_in = ColorRange.FULL
        else:
            range_in = ColorRange.LIMITED

    if ColorRange(range_in).is_limited:
        return 16 << get_depth(fmt) - 8

    return 0


def get_lowest_values(
    clip_or_depth: int | VideoFormatT | HoldsVideoFormatT,
    range_in: ColorRangeT | None = None, family: vs.ColorFamily | None = None
) -> Sequence[float]:
    """Get the lowest values of all planes of a specified format."""

    fmt = get_video_format(clip_or_depth)

    return normalize_seq([
        get_lowest_value(fmt, False, range_in, family),
        get_lowest_value(fmt, True, range_in, family)
    ], fmt.num_planes)


def get_neutral_value(clip_or_depth: int | VideoFormatT | HoldsVideoFormatT) -> float:
    """
    Returns the neutral point value (e.g. as used by std.MakeDiff) for the specified bit depth,
    or bit depth of the clip/format specified.

    :param clip_or_depth:   Input bit depth, or clip, frame, format from where to get it.

    :return:                Neutral value.
    """

    fmt = get_video_format(clip_or_depth)

    if fmt.sample_type is vs.FLOAT:
        return 0.0

    return 1 << (get_depth(fmt) - 1)


def get_neutral_values(clip_or_depth: int | VideoFormatT | HoldsVideoFormatT) -> Sequence[float]:
    """Get the neutral values of all planes of a specified format."""

    fmt = get_video_format(clip_or_depth)
    return normalize_seq(get_neutral_value(fmt), fmt.num_planes)


def get_peak_value(
    clip_or_depth: int | VideoFormatT | HoldsVideoFormatT, chroma: bool = False,
    range_in: ColorRangeT | None = None, family: vs.ColorFamily | None = None
) -> float:
    """
    Returns the peak value for the specified bit depth, or bit depth of the clip/format specified.

    :param clip_or_depth:   Input bit depth, or clip, frame, format from where to get it.
    :param chroma:          Whether to get luma (default) or chroma plane value.
    :param range_in:        Whether to get limited or full range peak value.
    :param family:          Which color family to assume for calculations.

    :return:                Highest possible value.
    """

    fmt = get_video_format(clip_or_depth)

    if fmt.sample_type is vs.FLOAT:
        return 0.5 if chroma else 1.0

    if (is_rgb := vs.RGB in (fmt.color_family, family)):
        chroma = False

    if range_in is None:
        if isinstance(clip_or_depth, vs.VideoNode):
            range_in = ColorRange(clip_or_depth)
        elif is_rgb:
            range_in = ColorRange.FULL
        else:
            range_in = ColorRange.LIMITED

    if ColorRange(range_in).is_limited:
        return (240 if chroma else 235) << get_depth(fmt) - 8

    return (1 << get_depth(fmt)) - 1


def get_peak_values(
    clip_or_depth: int | VideoFormatT | HoldsVideoFormatT,
    range_in: ColorRangeT | None = None, family: vs.ColorFamily | None = None
) -> Sequence[float]:
    """Get the peak values of all planes of a specified format."""

    fmt = get_video_format(clip_or_depth)

    return normalize_seq([
        get_peak_value(fmt, False, range_in, family),
        get_peak_value(fmt, True, range_in, family)
    ], fmt.num_planes)
