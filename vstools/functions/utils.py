from __future__ import annotations

import string
from typing import Any, Literal, Sequence, cast, overload
from weakref import WeakValueDictionary

import vapoursynth as vs

from ..enums import ColorRange, ColorRangeT, CustomStrEnum, Matrix
from ..exceptions import ClipLengthError, CustomIndexError, CustomValueError, InvalidColorFamilyError
from ..types import HoldsVideoFormatT, VideoFormatT
from .check import disallow_variable_format

__all__ = [
    'EXPR_VARS',

    'DitherType',

    'depth', 'depth_func',

    'frame2clip',

    'get_y', 'get_u', 'get_v',
    'get_r', 'get_g', 'get_b',

    'insert_clip',

    'plane',
    'join', 'split',
]


EXPR_VARS = (alph := list(string.ascii_lowercase))[(idx := alph.index('x')):] + alph[:idx]


class DitherType(CustomStrEnum):
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
        in_fmt: VideoFormatT | HoldsVideoFormatT, out_fmt: VideoFormatT | HoldsVideoFormatT, /,
        in_range: ColorRangeT | None = None, out_range: ColorRangeT | None = None
    ) -> bool:
        ...

    @overload
    @staticmethod
    def should_dither(
        in_bits: int, out_bits: int, /,
        in_sample_type: vs.SampleType | None = None, out_sample_type: vs.SampleType | None = None,
        in_range: ColorRangeT | None = None, out_range: ColorRangeT | None = None
    ) -> bool:
        ...

    @staticmethod  # type: ignore
    def should_dither(
        in_bits_or_fmt: int | VideoFormatT | HoldsVideoFormatT,
        out_bits_or_fmt: int | VideoFormatT | HoldsVideoFormatT, /,
        in_sample_type_or_range: vs.SampleType | ColorRangeT | None = None,
        out_sample_type_or_range: vs.SampleType | ColorRangeT | None = None,
        in_range: ColorRangeT | None = None, out_range: ColorRangeT | None = None,
    ) -> bool:
        from ..utils import get_video_format

        in_fmt = get_video_format(in_bits_or_fmt, sample_type=in_sample_type_or_range)
        out_fmt = get_video_format(out_bits_or_fmt, sample_type=out_sample_type_or_range)

        in_range = ColorRange.from_param(in_range, (DitherType.should_dither, 'in_range'))
        out_range = ColorRange.from_param(out_range, (DitherType.should_dither, 'out_range'))

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
    dither_type: str | DitherType = DitherType.AUTO,
) -> vs.VideoNode:
    from ..utils import get_video_format

    in_fmt = get_video_format(clip)
    out_fmt = get_video_format(bitdepth, sample_type=sample_type)

    range_out = ColorRange.from_param(range_out)
    range_in = ColorRange.from_param(range_in)

    if (
        in_fmt.bits_per_sample, in_fmt.sample_type, range_in
    ) == (
        out_fmt.bits_per_sample, out_fmt.sample_type, range_out
    ):
        return clip

    dither_type = DitherType(dither_type)

    if dither_type is DitherType.AUTO:
        should_dither = DitherType.should_dither(in_fmt, out_fmt, range_in, range_out)

        dither_type = DitherType.ERROR_DIFFUSION if should_dither else DitherType.NONE

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


@overload
def join(luma: vs.VideoNode, chroma: vs.VideoNode, family: vs.ColorFamily | None = None) -> vs.VideoNode:
    ...


@overload
def join(y: vs.VideoNode, u: vs.VideoNode, v: vs.VideoNode, family: Literal[vs.ColorFamily.YUV]) -> vs.VideoNode:
    ...


@overload
def join(
    y: vs.VideoNode, u: vs.VideoNode, v: vs.VideoNode, alpha: vs.VideoNode, family: Literal[vs.ColorFamily.YUV]
) -> vs.VideoNode:
    ...


@overload
def join(
    r: vs.VideoNode, g: vs.VideoNode, b: vs.VideoNode, family: Literal[vs.ColorFamily.RGB]
) -> vs.VideoNode:
    ...


@overload
def join(
    r: vs.VideoNode, g: vs.VideoNode, b: vs.VideoNode, alpha: vs.VideoNode, family: Literal[vs.ColorFamily.RGB]
) -> vs.VideoNode:
    ...


@overload
def join(*planes: vs.VideoNode, family: vs.ColorFamily | None = None) -> vs.VideoNode:
    ...


@overload
def join(planes: Sequence[vs.VideoNode], family: vs.ColorFamily | None = None) -> vs.VideoNode:
    ...


def join(*_planes: Any, **kwargs: Any) -> vs.VideoNode:
    from ..utils import get_color_family, get_video_format

    family: vs.ColorFamily | None = kwargs.get('family', None)

    if isinstance(_planes[-1], vs.ColorFamily):
        family = _planes[-1]
        _planes = _planes[:-1]

    planes = list[vs.VideoNode](_planes[0] if isinstance(_planes[0], list) else _planes)

    n_clips = len(planes)

    if not n_clips:
        raise CustomIndexError('Not enough clips/planes passed!', join)

    if n_clips == 1 and (family is None or family is (planes[0].format and planes[0].format.color_family)):
        return planes[0]

    if family is None:
        family = get_color_family(planes[0])

    if n_clips == 2:
        other_family = get_color_family(planes[1])

        if family in {vs.GRAY, vs.YUV}:
            InvalidColorFamilyError.check(
                other_family, vs.YUV, join, '"chroma" clip must be {correct} color family, not {wrong}!'
            )

            if family is vs.GRAY:
                planes[0] = get_y(planes[0])

            return vs.core.std.ShufflePlanes(planes, [0, 1, 2], other_family)

    if n_clips in {3, 4}:
        if family is vs.GRAY:
            for plane in planes[:3]:
                if (fmt := get_video_format(plane)).num_planes > 1:
                    family = fmt.color_family
                    break
            else:
                matrix = Matrix.from_video(planes[0])
                family = vs.RGB if matrix is Matrix.RGB else vs.YUV

        clip = vs.core.std.ShufflePlanes(planes[:3], [0, 0, 0], family)

        if n_clips == 4:
            clip = clip.std.ClipToProp(planes[-1], '_Alpha')

        return clip
    elif n_clips > 4:
        raise CustomValueError('Too many clips or planes passed!', join)

    raise CustomValueError('Not enough clips or planes passed!', join)


@disallow_variable_format
def plane(clip: vs.VideoNode, index: int, /, strict: bool = True) -> vs.VideoNode:
    assert clip.format

    if clip.format.num_planes == 1 and index == 0:
        return clip

    if not strict:
        if clip.format.color_family is vs.RGB:
            clip = clip.std.RemoveFrameProps('_Matrix')

    return vs.core.std.ShufflePlanes(clip, index, vs.GRAY)


@disallow_variable_format
def split(clip: vs.VideoNode, /) -> list[vs.VideoNode]:
    assert clip.format
    return [clip] if clip.format.num_planes == 1 else cast(list[vs.VideoNode], clip.std.SplitPlanes())


depth_func = depth
