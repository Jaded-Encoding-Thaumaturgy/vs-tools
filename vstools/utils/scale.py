from __future__ import annotations

from typing import Literal, Sequence, overload

import vapoursynth as vs
from stgpytools import normalize_seq

from ..enums import ColorRange, ColorRangeT
from ..types import HoldsVideoFormatT, VideoFormatT
from .info import get_depth, get_video_format

__all__ = [
    'scale_8bit', 'scale_value',

    'get_lowest_value', 'get_neutral_value', 'get_peak_value',
    'get_lowest_values', 'get_neutral_values', 'get_peak_values',
]


def scale_8bit(clip: VideoFormatT | HoldsVideoFormatT, value: int, chroma: bool = False) -> float:
    """
    Scale from an 8-bit value.

    :param clip:        Input clip, frame, or value representing a bitdepth.
    :param value:       Value to scale.
    :param chroma:      Values are chroma ranges, and must be converted as such. Default: False.

    :return:            Value scaled to the clip's bit-depth.
    """

    fmt = get_video_format(clip)

    if fmt.sample_type is vs.FLOAT:
        out = value / 255

        if chroma:
            out -= .5

        return out

    return value << get_depth(fmt) - 8


@overload
def scale_value(  # type: ignore
    value: int | float,
    input_depth: int | VideoFormatT | HoldsVideoFormatT,
    output_depth: Literal[8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31],
    range_in: ColorRangeT = ColorRange.LIMITED,
    range_out: ColorRangeT | None = None,
    scale_offsets: bool = False,
    chroma: bool = False
) -> int:
    ...


@overload
def scale_value(
    value: int | float,
    input_depth: int | VideoFormatT | HoldsVideoFormatT,
    output_depth: Literal[32],
    range_in: ColorRangeT = ColorRange.LIMITED,
    range_out: ColorRangeT | None = None,
    scale_offsets: bool = False,
    chroma: bool = False
) -> float:
    ...


@overload
def scale_value(
    value: int | float,
    input_depth: int | VideoFormatT | HoldsVideoFormatT,
    output_depth: int | VideoFormatT | HoldsVideoFormatT,
    range_in: ColorRangeT = ColorRange.LIMITED,
    range_out: ColorRangeT | None = None,
    scale_offsets: bool = False,
    chroma: bool = False
) -> float:
    ...


def scale_value(
    value: int | float,
    input_depth: int | VideoFormatT | HoldsVideoFormatT,
    output_depth: int | VideoFormatT | HoldsVideoFormatT,
    range_in: ColorRangeT = ColorRange.LIMITED,
    range_out: ColorRangeT | None = None,
    scale_offsets: bool = False,
    chroma: bool = False
) -> float:
    """
    Returns the peak value for the specified bit depth, or bit depth of the clip/format specified.

    :param value:           Value to scale.
    :param input_depth:     Input bit depth, or clip, frame, format from where to get it.
    :param output_depth:    Output bit depth, or clip, frame, format from where to get it.
    :param range_in:        Color range of the input value
    :param range_out:       Color range of the desired output.
    :param scale_offsets:   Whether or not to apply YUV offsets to float chroma and/or TV range integer values.
    :param chroma:          Whether or not to treat values as chroma values instead of luma.

    :return:                Scaled value.
    """

    out_value = float(value)

    in_fmt = get_video_format(input_depth)
    out_fmt = get_video_format(output_depth)

    if in_fmt.sample_type is vs.FLOAT:
        range_in = ColorRange.FULL
    else:
        range_in = ColorRange(range_in)

    if in_fmt.sample_type is vs.FLOAT:
        range_out = ColorRange.FULL
    elif range_out is not None:
        range_out = ColorRange(range_out)
    else:
        range_out = range_in

    if input_depth == output_depth and range_in == range_out:
        return out_value

    input_peak = get_peak_value(in_fmt, chroma, range_in)
    output_peak = get_peak_value(out_fmt, chroma, range_out)

    if scale_offsets:
        if out_fmt.sample_type is vs.FLOAT and chroma:
            out_value -= 128 << (in_fmt.bits_per_sample - 8)
        elif range_out.is_full and range_in.is_limited:
            out_value -= 16 << (in_fmt.bits_per_sample - 8)

    out_value *= output_peak / input_peak

    if scale_offsets:
        if in_fmt.sample_type is vs.FLOAT and chroma:
            out_value += 128 << (out_fmt.bits_per_sample - 8)
        elif range_in.is_full and range_out.is_limited:
            out_value += 16 << (out_fmt.bits_per_sample - 8)

    return out_value


def get_lowest_value(
    clip_or_depth: int | VideoFormatT | HoldsVideoFormatT, chroma: bool = False,
    range_in: ColorRangeT = ColorRange.FULL
) -> float:
    """
    Returns the lowest value for the specified bit depth, or bit depth of the clip/format specified.

    :param clip_or_depth:   Input bit depth, or clip, frame, format from where to get it.
    :param chroma:          Whether to get luma (default) or chroma plane value.
    :param range_in:        Whether to get limited or full range lowest value.

    :return:                Lowest possible value.
    """

    fmt = get_video_format(clip_or_depth)

    if ColorRange(range_in).is_limited:
        return scale_8bit(fmt, 16, chroma)

    if chroma and fmt.sample_type == vs.FLOAT:
        return -0.5

    return 0.


def get_lowest_values(
    clip_or_depth: int | VideoFormatT | HoldsVideoFormatT, range_in: ColorRangeT = ColorRange.FULL
) -> Sequence[float]:
    """Get all planes lowest values of a format."""

    fmt = get_video_format(clip_or_depth)

    return normalize_seq([
        get_lowest_value(fmt, False, range_in),
        get_lowest_value(fmt, True, range_in)
    ], fmt.num_planes)


def get_neutral_value(clip_or_depth: int | VideoFormatT | HoldsVideoFormatT, chroma: bool = False) -> float:
    """
    Returns the mid point value for the specified bit depth, or bit depth of the clip/format specified.

    :param clip_or_depth:   Input bit depth, or clip, frame, format from where to get it.
    :param chroma:          Whether to get luma (default) or chroma plane value.

    :return:                Neutral value.
    """

    fmt = get_video_format(clip_or_depth)

    if fmt.sample_type == vs.FLOAT:
        return 0. if chroma else 0.5

    return float(1 << (get_depth(fmt) - 1))


def get_neutral_values(clip_or_depth: int | VideoFormatT | HoldsVideoFormatT) -> Sequence[float]:
    """Get all planes neutral values of a format."""

    fmt = get_video_format(clip_or_depth)
    return normalize_seq([get_neutral_value(fmt, False), get_neutral_value(fmt, True)], fmt.num_planes)


def get_peak_value(
    clip_or_depth: int | VideoFormatT | HoldsVideoFormatT, chroma: bool = False,
    range_in: ColorRangeT = ColorRange.FULL
) -> float:
    """
    Returns the peak value for the specified bit depth, or bit depth of the clip/format specified.

    :param clip_or_depth:   Input bit depth, or clip, frame, format from where to get it.
    :param chroma:          Whether to get luma (default) or chroma plane value.
    :param range_in:        Whether to get limited or full range peak value.

    :return:                Highest possible value.
    """

    fmt = get_video_format(clip_or_depth)

    if ColorRange(range_in).is_limited:
        return scale_8bit(fmt, 240 if chroma else 235, chroma)

    if fmt.sample_type == vs.FLOAT:
        return 0.5 if chroma else 1.

    return (1 << get_depth(fmt)) - 1.


def get_peak_values(
    clip_or_depth: int | VideoFormatT | HoldsVideoFormatT, range_in: ColorRangeT = ColorRange.FULL
) -> Sequence[float]:
    """Get all planes peak values of a format."""

    fmt = get_video_format(clip_or_depth)
    return normalize_seq([get_peak_value(fmt, False, range_in), get_peak_value(fmt, True, range_in)], fmt.num_planes)
