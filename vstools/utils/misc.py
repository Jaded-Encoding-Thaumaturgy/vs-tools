from __future__ import annotations

import inspect
from fractions import Fraction
from math import floor
from typing import Any, Callable, Iterable, TypeVar

import vapoursynth as vs

from ..exceptions import InvalidSubsamplingError
from .info import get_video_format

__all__ = [
    'change_fps',

    'match_clip',

    'padder',

    'pick_func_stype',

    'set_output'
]


def change_fps(clip: vs.VideoNode, fps: Fraction) -> vs.VideoNode:
    """
    Convert the framerate of a clip.

    This is different from AssumeFPS as this will actively adjust
    the framerate of a clip, not simply set one.

    :param clip:        Input clip.
    :param fps:         Framerate to convert the clip to. Must be a Fration.

    :return:            Clip with the framerate converted and frames adjusted as necessary.
    """

    src_num, src_den = clip.fps_num, clip.fps_den
    dest_num, dest_den = fps.as_integer_ratio()

    if (dest_num, dest_den) == (src_num, src_den):
        return clip

    factor = (dest_num / dest_den) * (src_den / src_num)

    new_fps_clip = clip.std.BlankClip(
        length=floor(clip.num_frames * factor), fpsnum=dest_num, fpsden=dest_den
    )

    return new_fps_clip.std.FrameEval(lambda n: clip[round(n / factor)])


def match_clip(
    clip: vs.VideoNode, ref: vs.VideoNode, dimensions: bool = True,
    vformat: bool = True, matrices: bool = True, length: bool = False
) -> vs.VideoNode:
    from ..enums import Matrix, Primaries, Transfer
    from ..functions import check_variable

    assert check_variable(clip, match_clip)
    assert check_variable(ref, match_clip)

    clip = clip * ref.num_frames if length else clip
    clip = clip.resize.Bicubic(ref.width, ref.height) if dimensions else clip

    if vformat:
        assert ref.format
        clip = clip.resize.Bicubic(format=ref.format.id, matrix=Matrix.from_video(ref))

    if matrices:
        ref_frame = ref.get_frame(0)
        clip = clip.std.SetFrameProps(
            _Matrix=Matrix(ref_frame), _Transfer=Transfer(ref_frame), _Primaries=Primaries(ref_frame)
        )

    return clip.std.AssumeFPS(fpsnum=ref.fps.numerator, fpsden=ref.fps.denominator)


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
    from ..functions import check_variable
    from ..utils import core

    assert check_variable(clip, padder)

    width = clip.width + left + right
    height = clip.height + top + bottom

    fmt = get_video_format(clip)

    if (width % (1 << fmt.subsampling_w) != 0) or (height % (1 << fmt.subsampling_h) != 0):
        raise InvalidSubsamplingError(
            padder, fmt, 'Values must result in a mod congruent to the clip\'s subsampling ({subsampling})!'
        )

    reflected = core.resize.Point(
        clip.std.CopyFrameProps(clip.std.BlankClip()), width, height,
        src_top=-top, src_left=-left,
        src_width=width, src_height=height
    ).std.CopyFrameProps(clip)

    if reflect:
        return reflected

    return core.fb.FillBorders(  # type: ignore
        reflected, left=left, right=right, top=top, bottom=bottom
    )


FINT = TypeVar('FINT', bound=Callable[..., vs.VideoNode])
FFLOAT = TypeVar('FFLOAT', bound=Callable[..., vs.VideoNode])


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


def set_output(
    node: vs.RawNode | Iterable[vs.RawNode | Iterable[vs.RawNode | Iterable[vs.RawNode]]],
    name: str | bool = True, **kwargs: Any
) -> None:
    """Set output node with optional name, and if available, use vspreview set_output."""
    from ..functions import flatten_vnodes

    last_index = len(vs.get_outputs())

    ref_id = str(id(node))

    title = 'Node'

    if isinstance(node, Iterable):
        node = list[vs.RawNode](flatten_vnodes(node))  # type: ignore
        index = ''
    else:
        index = ' ' + str(last_index)

    checktype = node[0] if isinstance(node, list) else node

    if isinstance(checktype, vs.VideoNode):
        title = 'Clip'
    elif isinstance(checktype, vs.AudioNode):
        title = 'Audio'

    if (not name and name is not False) or name is True:
        name = f"{title}{index}"

        current_frame = inspect.currentframe()

        assert current_frame
        assert current_frame.f_back

        for vname, val in reversed(current_frame.f_back.f_locals.items()):
            if (str(id(val)) == ref_id):
                name = vname
                break

    try:
        from vspreview import set_output as vsp_set_output
        if isinstance(node, list):
            for idx, n in enumerate(node, 0 if index else last_index):
                vsp_set_output(n, name and f'{name} {idx}', **kwargs)
        else:
            vsp_set_output(node, name, **kwargs)
    except ModuleNotFoundError:
        for idx, n in enumerate(node if isinstance(node, list) else [node], last_index):
            n.set_output(idx)
