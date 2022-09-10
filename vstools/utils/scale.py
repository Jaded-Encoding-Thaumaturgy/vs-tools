from __future__ import annotations

import vapoursynth as vs

from ..enums import ColorRange, ColorRangeT
from ..exceptions import CustomIndexError
from ..functions import disallow_variable_format
from ..types import HoldsVideoFormatT
from .info import get_depth, get_format

__all__ = [
    'scale_8bit', 'scale_thresh', 'scale_value',

    'get_lowest_value', 'get_neutral_value', 'get_peak_value'
]


def scale_8bit(clip: HoldsVideoFormatT, value: float, chroma: bool = False) -> float:
    """
    Scale to an 8-bit value.

    :param clip:        Input clip, frame, or value representing a bitdepth.
    :param value:       Value to scale.
    :param chroma:      Values are chroma ranges, and must be converted as such.
                        Default: False.

    :return:            Value scaled to 8-bit.
    """
    fmt = get_format(clip)

    if fmt.sample_type is vs.FLOAT:
        value /= 255

        if chroma:
            value -= .5
    else:
        value = float(int(value) << get_depth(fmt) - 8)

    return value


def scale_thresh(
    thresh: float, clip: HoldsVideoFormatT, assume: int | None = None, peak: int | float | None = None
) -> float:
    """
    Scale thresholds from float to int or vice versa.

    :param thresh:              Threshold to scale.
    :param clip:                Input clip.
    :param assume:              @@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS
    :param peak:                Peak value of the clip.

    :return:                    Scaled value.

    :raises CustomValueError:   Threshold is not positive.
    """
    fmt = get_format(clip)

    if thresh < 0:
        raise CustomIndexError('Thresholds must be positive!', scale_thresh)

    peak = get_peak_value(fmt, False) if peak is None else peak

    if fmt.sample_type == vs.FLOAT or thresh > 1 and not assume:
        return thresh

    if assume:
        return round(thresh / ((1 << assume) - 1) * peak)

    return round(thresh * peak)


def scale_value(
    value: int | float,
    input_depth: int | HoldsVideoFormatT,
    output_depth: int | HoldsVideoFormatT,
    range_in: ColorRangeT = ColorRange.LIMITED,
    range_out: ColorRangeT | None = None,
    scale_offsets: bool = False,
    chroma: bool = False
) -> float:
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    out_value = float(value)

    in_fmt = get_format(input_depth)
    out_fmt = get_format(output_depth)

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

    value *= output_peak / input_peak

    if scale_offsets:
        if in_fmt.sample_type is vs.FLOAT and chroma:
            out_value += 128 << (out_fmt.bits_per_sample - 8)
        elif range_in.is_full and range_out.is_limited:
            out_value += 16 << (out_fmt.bits_per_sample - 8)

    return value


@disallow_variable_format
def get_lowest_value(
    clip_or_depth: int | HoldsVideoFormatT, chroma: bool = False, range: ColorRangeT = ColorRange.FULL
) -> float:
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    fmt = get_format(clip_or_depth)

    if ColorRange(range).is_limited:
        return scale_8bit(fmt, 16, chroma)

    if chroma and fmt.sample_type == vs.FLOAT:
        return -0.5

    return 0.


@disallow_variable_format
def get_neutral_value(clip_or_depth: int | HoldsVideoFormatT, chroma: bool = False) -> float:
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    fmt = get_format(clip_or_depth)

    if fmt.sample_type == vs.FLOAT:
        return 0. if chroma else 0.5

    return float(1 << (get_depth(fmt) - 1))


@disallow_variable_format
def get_peak_value(
    clip_or_depth: int | HoldsVideoFormatT, chroma: bool = False, range_in: ColorRangeT = ColorRange.FULL
) -> float:
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    fmt = get_format(clip_or_depth)

    if ColorRange(range_in).is_limited:
        return scale_8bit(fmt, 240 if chroma else 235, chroma)

    if fmt.sample_type == vs.FLOAT:
        return 0.5 if chroma else 1.

    return (1 << get_depth(fmt)) - 1.
