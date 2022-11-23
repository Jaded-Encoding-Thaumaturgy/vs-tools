from __future__ import annotations

import inspect
from fractions import Fraction
from math import floor
from typing import Callable, TypeVar

import vapoursynth as vs

from ..exceptions import InvalidSubsamplingError
from ..functions import disallow_variable_format, disallow_variable_resolution, to_arr
from .info import get_video_format

__all__ = [
    'change_fps',

    'padder',

    'pick_func_stype',

    'set_output'
]


def change_fps(clip: vs.VideoNode, fps: Fraction) -> vs.VideoNode:
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
    width = clip.width + left + right
    height = clip.height + top + bottom

    fmt = get_video_format(clip)

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
    assert clip.format

    return func_float if clip.format.sample_type == vs.FLOAT else func_int


def set_output(clip: vs.VideoNode, text: bool | int | str | tuple[int, int] | tuple[int, int, str] = True) -> None:
    index = len(vs.get_outputs())

    ref_id = str(id(clip))
    arr = to_arr(text)

    if any([isinstance(x, str) for x in arr]):
        ref_name = arr[-1]
    else:
        ref_name = f"Clip {index}"

        current_frame = inspect.currentframe()

        assert current_frame
        assert current_frame.f_back

        for x in current_frame.f_back.f_locals.items():
            if (str(id(x[1])) == ref_id):
                ref_name = x[0]
                break

            ref_name = ref_name.title()
        ref_name = ref_name.title()

    if isinstance(text, tuple):
        pos, scale, title = (*text, ref_name)[:3]
    elif isinstance(text, int) and text is not True:
        pos, scale, title = (text, 2, ref_name)
    else:
        pos, scale, title = (7, 2, ref_name)

    if text:
        clip = clip.text.Text(title, pos, scale)

    clip = clip.std.SetFrameProp('Name', data=title)

    clip.set_output(index)
