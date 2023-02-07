from __future__ import annotations

import vapoursynth as vs

from ..enums import SceneChangeMode
from ..types import Sentinel
from .render import clip_async_render

__all__ = [
    'find_scene_changes'
]


def find_scene_changes(clip: vs.VideoNode, mode: SceneChangeMode = SceneChangeMode.WWXD) -> list[int]:
    """
    Generate a list of scene changes (keyframes).

    Dependencies:

    * `vapoursynth-wwxd <https://github.com/dubhater/vapoursynth-wwxd>`_
    * `vapoursynth-scxvid <https://github.com/dubhater/vapoursynth-scxvid>`_

    :param clip:            Clip to search for scene changes. Will be rendered in its entirety.
    :param mode:            Scene change detection mode.
    :return:                List of scene changes.
    """
    from ..utils import get_prop

    clip = clip.resize.Bilinear(640, 360, format=vs.YUV420P8)
    clip = mode.ensure_presence(clip)

    frames = clip_async_render(
        clip, None, 'Detecting scene changes...', lambda n, f: Sentinel.check(
            n, all(get_prop(f, key, int) == 1 for key in mode.prop_keys)
        )
    )

    return sorted(list(Sentinel.filter(frames)))
