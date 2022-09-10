from __future__ import annotations

from enum import Enum
from typing import Sequence, cast, overload
from weakref import WeakValueDictionary

import vapoursynth as vs

from ..enums import ColorRange, ColorRangeT
from ..exceptions import ClipLengthError, InvalidColorFamilyError
from .check import disallow_variable_format

__all__ = [
    'Dither',

    'depth',

    'frame2clip',

    'get_y', 'get_u', 'get_v',
    'get_r', 'get_g', 'get_b',

    'insert_clip',

    'plane',
    'join', 'split',
]


class Dither(str, Enum):
    """
    Enum for `zimg_dither_type_e`.
    """

    AUTO = 'auto'
    """Choose automatically."""

    NONE = 'none'
    """Round to nearest."""

    ORDERED = 'ordered'
    """Bayer patterned dither."""

    RANDOM = 'random'
    """Pseudo-random noise of magnitude 0.5."""

    ERROR_DIFFUSION = 'error_diffusion'
    """Floyd-Steinberg error diffusion."""

    @overload
    @staticmethod
    def should_dither(
        in_fmt: vs.VideoFormat, out_fmt: vs.VideoFormat, /,
        in_range: ColorRange | None = None, out_range: ColorRange | None = None
    ) -> bool:
        ...

    @overload
    @staticmethod
    def should_dither(
        in_bits: int, out_bits: int, /,
        in_sample_type: vs.SampleType | None = None, out_sample_type: vs.SampleType | None = None,
        in_range: ColorRange | None = None, out_range: ColorRange | None = None
    ) -> bool:
        ...

    @staticmethod  # type: ignore
    def should_dither(
        in_bits_or_fmt: int | vs.VideoFormat, out_bits_or_fmt: int | vs.VideoFormat, /,
        in_sample_type_or_range: vs.SampleType | ColorRange | None = None,
        out_sample_type_or_range: vs.SampleType | ColorRange | None = None,
        in_range: int | ColorRange | None = None, out_range: int | ColorRange | None = None,
    ) -> bool:
        from ..utils import get_format

        in_fmt = get_format(in_bits_or_fmt, sample_type=in_sample_type_or_range)
        out_fmt = get_format(out_bits_or_fmt, sample_type=out_sample_type_or_range)

        in_range = ColorRange.from_param(in_range, (Dither.should_dither, 'in_range'))
        out_range = ColorRange.from_param(out_range, (Dither.should_dither, 'out_range'))

        if out_fmt.sample_type is vs.FLOAT:
            return False

        if in_fmt.sample_type is vs.FLOAT:
            return True

        if in_range != out_range:
            return True

        in_bits = in_fmt.bits_per_sample
        out_bits = out_fmt.bits_per_sample

        if in_bits == out_bits:
            return False

        if in_bits > out_bits:
            return True

        return in_range == ColorRange.FULL and (in_bits, out_bits) != (8, 16)


@disallow_variable_format
def depth(
    clip: vs.VideoNode, bitdepth: int, /,
    sample_type: int | vs.SampleType | None = None, *,
    range_in: ColorRangeT | None = None, range_out: ColorRangeT | None = None,
    dither_type: str | Dither = Dither.AUTO,
) -> vs.VideoNode:
    from ..utils import get_format

    in_fmt = get_format(clip)
    out_fmt = get_format(bitdepth, sample_type=sample_type)

    range_out = ColorRange.from_param(range_out)
    range_in = ColorRange.from_param(range_in)

    if (
        in_fmt.bits_per_sample, in_fmt.sample_type, range_in
    ) == (
        out_fmt.bits_per_sample, out_fmt.sample_type, range_out
    ):
        return clip

    dither_type = Dither(dither_type)

    if dither_type is Dither.AUTO:
        should_dither = Dither.should_dither(in_fmt, out_fmt, range_in, range_out)

        dither_type = Dither.ERROR_DIFFUSION if should_dither else Dither.NONE

    new_format = in_fmt.replace(
        bits_per_sample=out_fmt.bits_per_sample, sample_type=out_fmt.sample_type
    )

    return clip.resize.Point(
        format=new_format.id, range_in=range_in, range=range_out, dither_type=dither_type
    )


_f2c_cache = WeakValueDictionary[int, vs.VideoNode]()


def frame2clip(frame: vs.VideoFrame) -> vs.VideoNode:
    key = hash((frame.width, frame.height, frame.format.id))

    if _f2c_cache.get(key, None) is None:
        _f2c_cache[key] = blank_clip = vs.core.std.BlankClip(
            None, frame.width, frame.height,
            frame.format.id, 1, 1, 1,
            [0] * frame.format.num_planes,
            True
        )
    else:
        blank_clip = _f2c_cache[key]

    frame_cp = frame.copy()

    return blank_clip.std.ModifyFrame(blank_clip, lambda n, f: frame_cp)


@disallow_variable_format
def get_y(clip: vs.VideoNode, /) -> vs.VideoNode:
    InvalidColorFamilyError.check(clip, [vs.YUV, vs.GRAY], get_y)

    return plane(clip, 0)


@disallow_variable_format
def get_u(clip: vs.VideoNode, /) -> vs.VideoNode:
    InvalidColorFamilyError.check(clip, vs.YUV, get_u)

    return plane(clip, 1)


@disallow_variable_format
def get_v(clip: vs.VideoNode, /) -> vs.VideoNode:
    InvalidColorFamilyError.check(clip, vs.YUV, get_v)

    return plane(clip, 2)


@disallow_variable_format
def get_r(clip: vs.VideoNode, /) -> vs.VideoNode:
    InvalidColorFamilyError.check(clip, vs.RGB, get_r)

    return plane(clip, 0)


@disallow_variable_format
def get_g(clip: vs.VideoNode, /) -> vs.VideoNode:
    InvalidColorFamilyError.check(clip, vs.RGB, get_g)

    return plane(clip, 1)


@disallow_variable_format
def get_b(clip: vs.VideoNode, /) -> vs.VideoNode:
    InvalidColorFamilyError.check(clip, vs.RGB, get_b)

    return plane(clip, 2)


def insert_clip(clip: vs.VideoNode, /, insert: vs.VideoNode, start_frame: int) -> vs.VideoNode:
    if start_frame == 0:
        return insert + clip[insert.num_frames:]

    pre = clip[:start_frame]

    frame_after_insert = start_frame + insert.num_frames

    if frame_after_insert > clip.num_frames:
        raise ClipLengthError('Inserted clip is too long.', insert_clip)

    if frame_after_insert == clip.num_frames:
        return pre + insert

    post = clip[start_frame + insert.num_frames:]

    return pre + insert + post


def join(planes: Sequence[vs.VideoNode], family: vs.ColorFamily = vs.YUV) -> vs.VideoNode:
    if len(planes) == 1 and family == vs.GRAY:
        return planes[0]

    return vs.core.std.ShufflePlanes(planes, [0, 0, 0], family)


@disallow_variable_format
def plane(clip: vs.VideoNode, planeno: int, /) -> vs.VideoNode:
    assert clip.format

    if clip.format.num_planes == 1 and planeno == 0:
        return clip

    if clip.format.color_family is vs.RGB:
        clip = clip.std.RemoveFrameProps('_Matrix')

    return vs.core.std.ShufflePlanes(clip, planeno, vs.GRAY)


@disallow_variable_format
def split(clip: vs.VideoNode, /) -> list[vs.VideoNode]:
    assert clip.format
    return [clip] if clip.format.num_planes == 1 else cast(list[vs.VideoNode], clip.std.SplitPlanes())
