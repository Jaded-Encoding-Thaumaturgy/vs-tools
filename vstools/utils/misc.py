from __future__ import annotations

from fractions import Fraction
from math import floor
from typing import Callable, TypeVar

import vapoursynth as vs

from ..exceptions import InvalidSubsamplingError
from ..functions import disallow_variable_format, disallow_variable_resolution
from .info import get_format

__all__ = [
    'change_fps',

    'padder',

    'pick_func_stype'
]


def change_fps(clip: vs.VideoNode, fps: Fraction) -> vs.VideoNode:
    """
    Convert the framerate of a clip.

    This is different from AssumeFPS as this will actively adjust
    the framerate of a clip, not simply set one.

    :param clip:        Input clip.
    :param fps:         Framerate to conver the clip to. Must be a Fration.

    :return:            Clip with the framerate converted and frames adjusted as necessary.
    """
    src_num, src_den = clip.fps_num, clip.fps_den
    dest_num, dest_den = fps.as_integer_ratio()

    if (dest_num, dest_den) == (src_num, src_den):
        return clip

    factor = (dest_num / dest_den) * (src_den / src_num)

    def _frame_adjuster(n: int) -> vs.VideoNode:
        original = floor(n / factor)
        return clip[original] * (clip.num_frames + 100)

    new_fps_clip = clip.std.BlankClip(
        length=floor(clip.num_frames * factor), fpsnum=dest_num, fpsden=dest_den
    )

    return new_fps_clip.std.FrameEval(_frame_adjuster)


@disallow_variable_format
@disallow_variable_resolution
def padder(
    clip: vs.VideoNode, left: int = 0, right: int = 0, top: int = 0, bottom: int = 0, reflect: bool = True
) -> vs.VideoNode:
    """
    Pad out the pixels on the side by the given amount of pixels.

    There are two padding modes:

        * Filling: This will simply duplicate the row/column *n* amount of pixels.
        * Reflect: This will reflect the clip for *n* amount of pixels.

    Default mode is `Reflect`. `Filling` can be enabled by setting `reflect=False`.

    Optional Dependencies:
        * `reflect=False`: `VapourSynth-fillborders <https://github.com/dubhater/vapoursynth-fillborders>`_

    For a 4:2:0 clip, the output must be an even resolution.

    :param clip:        Input clip.
    :param left:        Padding added to the left side of the clip.
    :param right:       Padding added to the right side of the clip.
    :param top:         Padding added to the top side of the clip.
    :param bottom:      Padding added to the bottom side of the clip.
    :param reflect:     Whether to reflect the padded pixels.
                        Default: True.
    """
    width = clip.width + left + right
    height = clip.height + top + bottom

    fmt = get_format(clip)

    if (width % (1 << fmt.subsampling_w) != 0) or (height % (1 << fmt.subsampling_h) != 0):
        raise InvalidSubsamplingError(
            padder, fmt, 'Values must result in a mod congruent to the clip\'s subsampling ({subsampling})!'
        )

    reflected = vs.core.resize.Point(
        clip, width, height,
        src_top=-top, src_left=-left,
        src_width=width, src_height=height
    )

    if reflect:
        return reflected

    return vs.core.fb.FillBorders(
        reflected, left=left, right=right, top=top, bottom=bottom
    )


FINT = TypeVar('FINT', bound=Callable[..., vs.VideoNode])
FFLOAT = TypeVar('FFLOAT', bound=Callable[..., vs.VideoNode])


@disallow_variable_format
@disallow_variable_resolution
def pick_func_stype(clip: vs.VideoNode, func_int: FINT, func_float: FFLOAT) -> FINT | FFLOAT:
    """
    Pick the function matching the sample type of the clip's format.

    :param clip:        Input clip.
    :param func_int:    Function to run on integer clips.
    :param func_float:  Function to run on float clips.

    :return:            Function matching the sample type of your clip's format.
    """
    assert clip.format
    return func_float if clip.format.sample_type == vs.FLOAT else func_int
