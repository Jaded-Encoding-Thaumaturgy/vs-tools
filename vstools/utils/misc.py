from __future__ import annotations

import inspect
from fractions import Fraction
from math import floor
from typing import Any, Callable, TypeVar

import vapoursynth as vs

from ..exceptions import InvalidSubsamplingError
from ..functions import disallow_variable_format, disallow_variable_resolution
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


def set_output(node: vs.RawNode, name: str | bool = True, **kwargs: Any) -> None:
    index = len(vs.get_outputs())

    ref_id = str(id(node))

    title = 'Node'

    if isinstance(node, vs.VideoNode):
        title = 'Clip'
    elif isinstance(node, vs.AudioNode):
        title = 'Audio'

    if not name or name is True:
        name = f"{title} {index}"

        current_frame = inspect.currentframe()

        assert current_frame
        assert current_frame.f_back

        for vname, val in reversed(current_frame.f_back.f_locals.items()):
            if (str(id(val)) == ref_id):
                name = vname
                break

    try:
        from vspreview import set_output
        set_output(node, name, **kwargs)
    except ModuleNotFoundError:
        if isinstance(name, str) and isinstance(node, vs.VideoNode):
            node = node.std.SetFrameProp('Name', data=name.title())  # type: ignore

        node.set_output(index)
