from __future__ import annotations

from typing import Any, Literal, overload

import vapoursynth as vs
from stgpytools import KwargsT
from vstools import PropEnum

from ..enums import ChromaLocation, ColorRange, Matrix, Primaries, Transfer
from ..enums.stubs import SelfPropEnum

__all__ = [
    'video_heuristics',

    'video_resample_heuristics'
]


@overload
def video_heuristics(
    clip: vs.VideoNode, props: vs.FrameProps | bool | None = None,
    prop_in: bool = True, assumed_return: Literal[False] = ...
) -> dict[str, int]:
    ...


@overload
def video_heuristics(
    clip: vs.VideoNode, props: vs.FrameProps | bool | None = None,
    prop_in: bool = True, assumed_return: Literal[True] = ...
) -> tuple[dict[str, int], list[str]]:
    ...


def video_heuristics(
    clip: vs.VideoNode, props: vs.FrameProps | bool | None = None,
    prop_in: bool = True, assumed_return: bool = False
) -> dict[str, int] | tuple[dict[str, int], list[str]]:
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

    assumed_props = list[str]()
    props_dict: vs.FrameProps | None
    heuristics = dict[str, PropEnum]()

    if props is True:
        with clip.get_frame(0) as frame:
            props_dict = frame.props.copy()
    else:
        props_dict = props or None

    def try_or_fallback(prop_type: type[SelfPropEnum]) -> SelfPropEnum:
        try:
            assert props_dict
            if prop_type.prop_key in props_dict:
                return prop_type.from_video(props_dict, True)
        except Exception:
            assumed_props.append(prop_type.prop_key)

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
            'transfer': Transfer.from_res(clip), 'range': ColorRange.from_res(clip),
            'chromaloc': ChromaLocation.from_res(clip)
        }

        assumed_props.extend(v.prop_key for v in heuristics.values())

    out_props = {f'{k}_in' if prop_in else k: v for k, v in heuristics.items()}

    if assumed_return:
        return (out_props, assumed_props)  # type: ignore

    return out_props  # type: ignore


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
