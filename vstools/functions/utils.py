from __future__ import annotations

from enum import Enum
from typing import Any, Literal, Sequence, cast, overload
from weakref import WeakValueDictionary

import vapoursynth as vs

from ..enums import ColorRange, ColorRangeT, Matrix
from ..exceptions import ClipLengthError, CustomIndexError, CustomValueError, InvalidColorFamilyError
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
        """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""

    @overload
    @staticmethod
    def should_dither(
        in_bits: int, out_bits: int, /,
        in_sample_type: vs.SampleType | None = None, out_sample_type: vs.SampleType | None = None,
        in_range: ColorRange | None = None, out_range: ColorRange | None = None
    ) -> bool:
        """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""

    @staticmethod  # type: ignore
    def should_dither(
        in_bits_or_fmt: int | vs.VideoFormat, out_bits_or_fmt: int | vs.VideoFormat, /,
        in_sample_type_or_range: vs.SampleType | ColorRange | None = None,
        out_sample_type_or_range: vs.SampleType | ColorRange | None = None,
        in_range: int | ColorRange | None = None, out_range: int | ColorRange | None = None,
    ) -> bool:
        """
        Automatically determines whether dithering is needed for a given depth/range/sample_type conversion.

        If an input range is specified, and output range *should* be specified
        otherwise it assumes a range conversion.

        For an explanation of when dithering is needed:
            - Dithering is NEVER needed if the conversion results in a float sample type.
            - Dithering is ALWAYS needed for a range conversion (i.e. full to limited or vice-versa).
            - Dithering is ALWAYS needed to convert a float sample type to an integer sample type.
            - Dithering is needed when upsampling full range content with the exception of 8 -> 16 bit upsampling,
              as this is a simple bitshift without rounding, (0-255) * 257 -> (0-65535).
            - Dithering is needed when downsampling limited or full range.

        Dithering is theoretically needed when converting from an integer depth greater than 10 to half float,
        despite the higher bit depth, but zimg's internal resampler currently does not dither for float output.

        :param in_bits_or_fmt:              Input bitdepth or video format.
        :param out_bits_or_fmt:             Output bitdepth or video format.
        :param in_sample_type_or_range:     Input sample type of color range.
        :param out_sample_type_or_range:    Output sample type of color range.
        :param in_range:                    Input color range.
        :param out_range:                   Output color range.

        :return:                            True if the clip should be dithered, else False.
        """
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
    """
    A convenience bitdepth conversion function using only internal plugins.

    .. code-block:: python

        >>> src_8 = vs.core.std.BlankClip(format=vs.YUV420P8)
        >>> src_10 = depth(src_8, 10)
        >>> src_10.format.name
        'YUV420P10'

    .. code-block:: python

        >>> src2_10 = vs.core.std.BlankClip(format=vs.RGB30)
        >>> src2_8 = depth(src2_10, 8, dither_type=Dither.RANDOM)  # override default dither behavior
        >>> src2_8.format.name
        'RGB24'

    :param clip:            Input clip.
    :param bitdepth:        Desired bitdepth of the output clip.
    :param sample_type:     Desired sample type of output clip. Allows overriding default float/integer behavior.
                            Accepts ``vapoursynth.SampleType`` enums ``vapoursynth.INTEGER`` and ``vapoursynth.FLOAT``
                            or their values, ``0`` and ``1`` respectively.
    :param range_in:       Input pixel range (defaults to input `clip`'s range).
    :param range_out:       Output pixel range (defaults to input `clip`'s range).
    :param dither_type:     Dithering algorithm. Allows overriding default dithering behavior. See :py:class:`Dither`.

                            Defaults to :attr:`Dither.ERROR_DIFFUSION`, or Floyd-Steinberg error diffusion,
                            when downsampling, converting between ranges, or upsampling full range input.
                            Defaults to :attr:`Dither.NONE`, or round to nearest, otherwise.
                            See :py:func:`Dither.should_dither` for more information.

    :return:                Converted clip with desired bit depth and sample type.
                            ``ColorFamily`` will be same as input.
    """
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
    """
    Convert a VideoFrame to a VideoNode.

    :param frame:       Input frame.

    :return:            1-frame long VideoNode of the input frame.
    """
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
    """
    Extract the luma (Y) plane of the given clip.

    :param clip:                Input clip.

    :return:                    Y plane of the input clip.

    :raises CustomValueError:   Clip is not GRAY or YUV.
    """
    InvalidColorFamilyError.check(clip, [vs.YUV, vs.GRAY], get_y)

    return plane(clip, 0)


@disallow_variable_format
def get_u(clip: vs.VideoNode, /) -> vs.VideoNode:
    """
    Extract the first chroma (U) plane of the given clip.

    :param clip:                Input clip.

    :return:                    Y plane of the input clip.

    :raises CustomValueError:   Clip is not YUV.
    """
    InvalidColorFamilyError.check(clip, vs.YUV, get_u)

    return plane(clip, 1)


@disallow_variable_format
def get_v(clip: vs.VideoNode, /) -> vs.VideoNode:
    """
    Extract the second chroma (V) plane of the given clip.

    :param clip:                Input clip.

    :return:                    V plane of the input clip.

    :raises CustomValueError:   Clip is not YUV.
    """
    InvalidColorFamilyError.check(clip, vs.YUV, get_v)

    return plane(clip, 2)


@disallow_variable_format
def get_r(clip: vs.VideoNode, /) -> vs.VideoNode:
    """
    Extract the red plane of the given clip.

    :param clip:                Input clip.

    :return:                    R plane of the input clip.

    :raises CustomValueError:   Clip is not RGB.
    """
    InvalidColorFamilyError.check(clip, vs.RGB, get_r)

    return plane(clip, 0)


@disallow_variable_format
def get_g(clip: vs.VideoNode, /) -> vs.VideoNode:
    """
    Extract the green plane of the given clip.

    :param clip:                Input clip.

    :return:                    G plane of the input clip.

    :raises CustomValueError:   Clip is not RGB.
    """
    InvalidColorFamilyError.check(clip, vs.RGB, get_g)

    return plane(clip, 1)


@disallow_variable_format
def get_b(clip: vs.VideoNode, /) -> vs.VideoNode:
    """
    Extract the blue plane of the given clip.

    :param clip:                Input clip.

    :return:                    B plane of the input clip.

    :raises CustomValueError:   Clip is not RGB.
    """
    InvalidColorFamilyError.check(clip, vs.RGB, get_b)

    return plane(clip, 2)


def insert_clip(clip: vs.VideoNode, /, insert: vs.VideoNode, start_frame: int) -> vs.VideoNode:
    """
    Replace frames of a longer clip with those of a shorter one.

    The insert clip may not go beyond the final frame of the input clip.

    :param clip:                Input clip.
    :param insert:              Clip to insert into the input clip.
    :param start_frame:         Frame to start inserting from.

    :return:                    Clip with frames replaced by the insert clip.

    :raises CustomValueError:   Insert clip is too long and goes beyond the input clip's final frame.
    """
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
    """
    Join a list of planes together to form a single RGB clip.

    :param luma:        Luma clip, GRAY or YUV.
    :param chroma:      Chroma clip, must be YUV.

    :return:            YUV clip of combined planes.
    """


@overload
def join(y: vs.VideoNode, u: vs.VideoNode, v: vs.VideoNode, family: vs.ColorFamily | None = None) -> vs.VideoNode:
    """
    Join a list of planes together to form a single RGB clip.

    :param y:           Y plane.
    :param u:           U plane.
    :param v:           V plane.

    :return:            YUV clip of combined planes.
    """


@overload
def join(
    y: vs.VideoNode, u: vs.VideoNode, v: vs.VideoNode, alpha: vs.VideoNode, family: Literal[vs.ColorFamily.YUV]
) -> vs.VideoNode:
    """
    Join a list of planes together to form a single RGB clip.

    :param y:           Y plane.
    :param u:           U plane.
    :param v:           V plane.
    :param alpha:       Alpha clip.

    :return:            YUV clip of combined planes with an alpha clip attached.
    """


@overload
def join(
    r: vs.VideoNode, g: vs.VideoNode, b: vs.VideoNode, family: Literal[vs.ColorFamily.RGB]
) -> vs.VideoNode:
    """
    Join a list of planes together to form a single RGB clip.

    :param r:           R plane.
    :param g:           G plane.
    :param b:           B plane.

    :return:            RGB clip of combined planes.
    """


@overload
def join(
    r: vs.VideoNode, g: vs.VideoNode, b: vs.VideoNode, alpha: vs.VideoNode, family: Literal[vs.ColorFamily.RGB]
) -> vs.VideoNode:
    """
    Join a list of planes together to form a single RGB clip.

    :param r:           R plane.
    :param g:           G plane.
    :param b:           B plane.
    :param alpha:       Alpha clip.

    :return:            RGB clip of combined planes with an alpha clip attached.
    """


@overload
def join(*planes: vs.VideoNode, family: vs.ColorFamily | None = None) -> vs.VideoNode:
    """
    Join a list of planes together to form a single clip.

    :param planes:      Planes to combine.
    :param family:      Output clip family.
                        Default: first clip or detected from props if GRAY and len(planes) > 1.

    :return:            Clip of combined planes.
    """


@overload
def join(planes: Sequence[vs.VideoNode], family: vs.ColorFamily | None = None) -> vs.VideoNode:
    """
    Join a list of planes together to form a single clip.

    :param planes:      Planes to combine.
    :param family:      Output clip family.
                        Default: first clip or detected from props if GRAY and len(planes) > 1.

    :return:            Clip of combined planes.
    """


def join(*_planes: Any, **kwargs: Any) -> vs.VideoNode:
    from ..utils import get_color_family, get_format

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
                if (fmt := get_format(plane)).num_planes > 1:
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
    """
    Extract a plane from the given clip.

    :param clip:        Input clip.
    :param index:       Index of the plane to extract.

    :return:            Grayscale clip of the clip's plane.
    """

    assert clip.format

    if clip.format.num_planes == 1 and index == 0:
        return clip

    if not strict:
        if clip.format.color_family is vs.RGB:
            clip = clip.std.RemoveFrameProps('_Matrix')

    return vs.core.std.ShufflePlanes(clip, index, vs.GRAY)


@disallow_variable_format
def split(clip: vs.VideoNode, /) -> list[vs.VideoNode]:
    """
    Split a clip into a list of individual planes.

    :param clip:    Input clip.

    :return:        List of individual planes.
    """
    assert clip.format
    return [clip] if clip.format.num_planes == 1 else cast(list[vs.VideoNode], clip.std.SplitPlanes())
