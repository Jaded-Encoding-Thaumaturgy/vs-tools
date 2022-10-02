from __future__ import annotations

from typing import overload

import vapoursynth as vs

from ..exceptions import UnsupportedSubsamplingError
from ..functions import depth, disallow_variable_format
from ..types import HoldsVideoFormatT, VideoFormatT
from .math import mod_x

__all__ = [
    'get_var_infos',
    'get_video_format',

    'get_depth', 'get_sample_type', 'get_subsampling', 'get_color_family',

    'expect_bits',

    'get_plane_sizes', 'get_resolutions',

    'get_w', 'get_h'
]


def get_var_infos(frame: vs.VideoNode | vs.VideoFrame) -> tuple[vs.VideoFormat, int, int]:
    if isinstance(frame, vs.VideoNode) and not (
        frame.width and frame.height and frame.format
    ):
        frame = frame.get_frame(0)

    assert frame.format

    return frame.format, frame.width, frame.height


@disallow_variable_format
def get_video_format(
    value: int | VideoFormatT | HoldsVideoFormatT, /, *, sample_type: int | vs.SampleType | None = None
) -> vs.VideoFormat:
    if sample_type is not None:
        sample_type = vs.SampleType(sample_type)

    if isinstance(value, vs.VideoFormat):
        return value

    if isinstance(value, vs.PresetFormat):
        return vs.core.get_video_format(value)

    if isinstance(value, int):
        if value > 32:
            return vs.core.get_video_format(value)

        if sample_type is None:
            sample_type = vs.SampleType(value == 32)

        return vs.core.query_video_format(vs.YUV, sample_type, value)

    assert value.format

    if sample_type is not None:
        return value.format.replace(sample_type=sample_type)

    return value.format


def get_depth(clip: VideoFormatT | HoldsVideoFormatT, /) -> int:
    return get_video_format(clip).bits_per_sample


def get_sample_type(clip: VideoFormatT | HoldsVideoFormatT | vs.SampleType, /) -> vs.SampleType:
    if isinstance(clip, vs.SampleType):
        return clip
    return get_video_format(clip).sample_type


def get_color_family(clip: VideoFormatT | HoldsVideoFormatT | vs.ColorFamily, /) -> vs.ColorFamily:
    if isinstance(clip, vs.ColorFamily):
        return clip
    return get_video_format(clip).color_family


def expect_bits(clip: vs.VideoNode, /, expected_depth: int = 16) -> tuple[vs.VideoNode, int]:
    bits = get_depth(clip)

    if bits != expected_depth:
        clip = depth(clip, expected_depth)

    return clip, bits


def get_plane_sizes(frame: vs.VideoNode | vs.VideoFrame, index: int, /) -> tuple[int, int]:
    assert frame.format and frame.width

    width, height = frame.width, frame.height

    if index != 0:
        width >>= frame.format.subsampling_w
        height >>= frame.format.subsampling_h

    return width, height


def get_resolutions(clip: vs.VideoNode | vs.VideoFrame) -> tuple[tuple[int, int, int], ...]:
    assert clip.format

    return tuple(
        (plane, *get_plane_sizes(clip, plane)) for plane in range(clip.format.num_planes)
    )


def get_subsampling(clip: VideoFormatT | HoldsVideoFormatT, /) -> str | None:
    fmt = get_video_format(clip)

    if fmt.color_family != vs.YUV:
        return None

    if fmt.subsampling_w == 2 and fmt.subsampling_h == 2:
        return '410'

    if fmt.subsampling_w == 2 and fmt.subsampling_h == 0:
        return '411'

    if fmt.subsampling_w == 1 and fmt.subsampling_h == 1:
        return '420'

    if fmt.subsampling_w == 1 and fmt.subsampling_h == 0:
        return '422'

    if fmt.subsampling_w == 0 and fmt.subsampling_h == 1:
        return '440'

    if fmt.subsampling_w == 0 and fmt.subsampling_h == 0:
        return '444'

    raise UnsupportedSubsamplingError('Unknown subsampling.', get_subsampling)


@overload
def get_w(height: float, ar: float = 16 / 9, /, mod: int = 2) -> int:
    ...


@overload
def get_w(height: float, ref: vs.VideoNode | vs.VideoFrame, /) -> int:
    ...


def get_w(height: float, ar_or_ref: vs.VideoNode | vs.VideoFrame | float = 16 / 9, /, mod: int | None = None) -> int:
    if isinstance(ar_or_ref, (vs.VideoNode, vs.VideoFrame)):
        assert (ref := ar_or_ref).format
        aspect_ratio = ref.width / ref.height
        mod = 1 << ref.format.subsampling_w
    else:
        aspect_ratio = ar_or_ref

        if mod is None:
            mod = 0 if height % 2 else 2

    width = height * aspect_ratio

    if mod:
        return mod_x(width, mod)

    return round(width)


@overload
def get_h(width: float, ar: float = 16 / 9, /, mod: int = 2) -> int:
    ...


@overload
def get_h(width: float, ref: vs.VideoNode | vs.VideoFrame, /) -> int:
    ...


def get_h(width: float, ar_or_ref: vs.VideoNode | vs.VideoFrame | float = 16 / 9, /, mod: int | None = None) -> int:
    if isinstance(ar_or_ref, (vs.VideoNode, vs.VideoFrame)):
        assert (ref := ar_or_ref).format
        aspect_ratio = ref.height / ref.width
        mod = 1 << ref.format.subsampling_h
    else:
        aspect_ratio = ar_or_ref

        if mod is None:
            mod = 0 if width % 2 else 2

    height = width * aspect_ratio

    if mod:
        return mod_x(height, mod)

    return round(height)
