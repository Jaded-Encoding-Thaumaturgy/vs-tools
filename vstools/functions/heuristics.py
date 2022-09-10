from __future__ import annotations

from enum import IntEnum

import vapoursynth as vs

from ..enums import ColorRange, Matrix, Primaries, Transfer

__all__ = [
    'video_heuristics'
]


def video_heuristics(clip: vs.VideoNode, props: vs.FrameProps | None = None, prop_in: bool = True) -> dict[str, int]:
    """
    Determine the video heuristics from the frame properties.

    :param clip:        Input clip.
    :param props:       FrameProps object. If None, obtains from input clip.
                        Default: None.
    :param prop_in:     Return the dict with keys in the form of `{prop_name}_in` parameter.
                        For example, `matrix_in` instead of `matrix`.
                        For more information, please refer to the
                        `Resize docs <https://www.vapoursynth.com/doc/functions/video/resize.html>`_.
                        Default: True.
    """
    heuristics = dict[str, IntEnum]()

    if props:
        heuristics |= {
            'matrix': Matrix.from_video(clip), 'primaries': Primaries.from_video(clip),
            'transfer': Transfer.from_video(clip), 'range': ColorRange.from_video(clip)
        }
    else:
        heuristics |= {
            'matrix': Matrix.from_res(clip), 'primaries': Primaries.from_res(clip),
            'transfer': Transfer.from_res(clip), 'range': ColorRange.LIMITED
        }

    return {f'{k}_in' if prop_in else k: v.value for k, v in heuristics.items()}
