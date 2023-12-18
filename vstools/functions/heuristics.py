from __future__ import annotations

from enum import IntEnum
from typing import Any

import vapoursynth as vs
from stgpytools import KwargsT

from ..enums import ChromaLocation, ColorRange, Matrix, Primaries, Transfer
from ..enums.stubs import SelfPropEnum

__all__ = [
    'video_heuristics',

    'video_resample_heuristics'
]


def video_heuristics(
    clip: vs.VideoNode, props: vs.FrameProps | bool | None = None, prop_in: bool = True
) -> dict[str, int]:
    """
    Determine the video heuristics from the frame properties.

    :param clip:        Input clip.
    :param props:       FrameProps object.
                        If true, it will grab props info from the clip.
                        If None/False, obtains from just from input clip.
                        Default: None.
    :param prop_in:     Return the dict with keys in the form of `{prop_name}_in` parameter.
                        For example, `matrix_in` instead of `matrix`.
                        For more information, please refer to the
                        `Resize docs <https://www.vapoursynth.com/doc/functions/video/resize.html>`_.
                        Default: True.

    :return:            A dict containing all the video heuristics that could be determined,
                        optionally using key names derived from the resize plugin.
    """

    props_dict: vs.FrameProps | None
    heuristics = dict[str, IntEnum]()

    if props is True:
        props_dict = clip.get_frame(0).props
    else:
        props_dict = props or None

    def try_or_fallback(prop_type: type[SelfPropEnum]) -> SelfPropEnum:
        try:
            assert props_dict
            if prop_type.prop_key in props_dict:
                return prop_type.from_video(props_dict, True)
        except Exception:
            ...

        return prop_type.from_video(clip)

    if props:
        heuristics |= {
            'matrix': try_or_fallback(Matrix), 'primaries': try_or_fallback(Primaries),
            'transfer': try_or_fallback(Transfer), 'range': try_or_fallback(ColorRange),
            'chromaloc': try_or_fallback(ChromaLocation)
        }
    else:
        heuristics |= {
            'matrix': Matrix.from_res(clip), 'primaries': Primaries.from_res(clip),
            'transfer': Transfer.from_res(clip), 'range': ColorRange.LIMITED,
            'chromaloc': ChromaLocation.from_res(clip)
        }

    return {f'{k}_in' if prop_in else k: v for k, v in heuristics.items()}


def video_resample_heuristics(clip: vs.VideoNode, kwargs: KwargsT | None = None, **fmt_kwargs: Any) -> KwargsT:
    """
    Get a kwargs object for a video's heuristics to pass to the resize plugin or Kernel.resample.

    :param clip:            Clip to derive the heuristics from.
    :param kwargs:          Keyword arguments for the _out parameters.
    :param fmt_kwargs:      Keyword arguments to pass to the output kwargs.
                            These will override any heuristics that were derived from the input clip!

    :return:                Keyword arguments to pass on to the resize plugin or Kernel.resample.
    """
    assert clip.format

    video_fmt = clip.format.replace(**fmt_kwargs)

    def_kwargs_in = video_heuristics(clip, False, True)
    def_kwargs_out = video_heuristics(clip.std.BlankClip(format=video_fmt.id), False, False)

    return KwargsT(format=video_fmt.id, **def_kwargs_in, **def_kwargs_out) | (kwargs or KwargsT())
