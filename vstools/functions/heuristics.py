from __future__ import annotations

from enum import IntEnum

import vapoursynth as vs

from ..enums import ChromaLocation, ColorRange, Matrix, Primaries, Transfer
from ..enums.stubs import SelfPropEnum

__all__ = [
    'video_heuristics'
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
