from __future__ import annotations

import vapoursynth as vs

from ..enums import ColorRange, ColorRangeT
from ..exceptions import CustomIndexError
from ..functions import disallow_variable_format
from ..types import HoldsVideoFormatT, VideoFormatT
from .info import get_depth, get_video_format

__all__ = [
    'scale_8bit', 'scale_thresh', 'scale_value',

    'get_lowest_value', 'get_neutral_value', 'get_peak_value',
    'get_lowest_values', 'get_neutral_values', 'get_peak_values',
]


def scale_8bit(clip: VideoFormatT | HoldsVideoFormatT, value: int, chroma: bool = False) -> float:
    fmt = get_video_format(clip)

    if fmt.sample_type is vs.FLOAT:
        out = value / 255

        if chroma:
            out -= .5

        return out

    return value << get_depth(fmt) - 8


def scale_thresh(
    thresh: float, clip: VideoFormatT | HoldsVideoFormatT,
    assume: int | None = None, peak: int | float | None = None
) -> float:
    fmt = get_video_format(clip)

    if thresh < 0:
        raise CustomIndexError('Thresholds must be positive!', scale_thresh)

    peak = get_peak_value(fmt, False) if peak is None else peak

    if fmt.sample_type == vs.FLOAT or thresh > 1 and not assume:
        return thresh

    if assume:
        return round(thresh / (get_peak_value(assume) * peak))

    return round(thresh * peak)


def scale_value(
    value: int | float,
    input_depth: int | VideoFormatT | HoldsVideoFormatT,
    output_depth: int | VideoFormatT | HoldsVideoFormatT,
    range_in: ColorRangeT = ColorRange.LIMITED,
    range_out: ColorRangeT | None = None,
    scale_offsets: bool = False,
    chroma: bool = False
) -> float:
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


@disallow_variable_format
def get_lowest_value(
    clip_or_depth: int | VideoFormatT | HoldsVideoFormatT, chroma: bool = False,
    range_in: ColorRangeT = ColorRange.FULL
) -> float:
    fmt = get_video_format(clip_or_depth)

    if ColorRange(range_in).is_limited:
        return scale_8bit(fmt, 16, chroma)

    if chroma and fmt.sample_type == vs.FLOAT:
        return -0.5

    return 0.


@disallow_variable_format
def get_lowest_values(
    clip_or_depth: int | VideoFormatT | HoldsVideoFormatT, range_in: ColorRangeT = ColorRange.FULL
) -> Sequence[float]:
    fmt = get_video_format(clip_or_depth)
    return normalize_seq(
        [get_lowest_value(fmt, False, range_in),
         get_lowest_value(fmt, True, range_in)],
        fmt.num_planes)


@disallow_variable_format
def get_neutral_value(clip_or_depth: int | VideoFormatT | HoldsVideoFormatT, chroma: bool = False) -> float:
    fmt = get_video_format(clip_or_depth)

    if fmt.sample_type == vs.FLOAT:
        return 0. if chroma else 0.5

    return float(1 << (get_depth(fmt) - 1))


@disallow_variable_format
def get_neutral_values(clip_or_depth: int | VideoFormatT | HoldsVideoFormatT) -> Sequence[float]:
    fmt = get_video_format(clip_or_depth)
    return normalize_seq([get_neutral_value(fmt, False), get_neutral_value(fmt, True)], fmt.num_planes)


@disallow_variable_format
def get_peak_value(
    clip_or_depth: int | VideoFormatT | HoldsVideoFormatT, chroma: bool = False,
    range_in: ColorRangeT = ColorRange.FULL
) -> float:
    fmt = get_video_format(clip_or_depth)

    if ColorRange(range_in).is_limited:
        return scale_8bit(fmt, 240 if chroma else 235, chroma)

    if fmt.sample_type == vs.FLOAT:
        return 0.5 if chroma else 1.

    return (1 << get_depth(fmt)) - 1.


@disallow_variable_format
def get_peak_values(
    clip_or_depth: int | VideoFormatT | HoldsVideoFormatT, range_in: ColorRangeT = ColorRange.FULL
) -> Sequence[float]:
    fmt = get_video_format(clip_or_depth)
    return normalize_seq([get_peak_value(fmt, False, range_in), get_peak_value(fmt, True, range_in)], fmt.num_planes)
