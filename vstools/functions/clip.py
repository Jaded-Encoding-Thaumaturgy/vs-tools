from __future__ import annotations

import vapoursynth as vs

from ..exceptions import FramesLengthError
from ..types import F_VD, FrameRange
from .normalize import normalize_franges

__all__ = [
    'shift_clip', 'shift_clip_multi',

    'process_var_clip'
]


def shift_clip(clip: vs.VideoNode, offset: int) -> vs.VideoNode:
    if offset > clip.num_frames - 1:
        raise FramesLengthError(shift_clip, 'offset')

    if offset < 0:
        return clip[0] * abs(offset) + clip[:offset]

    if offset > 0:
        return clip[offset:] + clip[-1] * offset

    return clip


def shift_clip_multi(clip: vs.VideoNode, offsets: FrameRange = (-1, 1)) -> list[vs.VideoNode]:
    ranges = normalize_franges(offsets)

    return [shift_clip(clip, x) for x in ranges]


def process_var_clip(clip: vs.VideoNode, function: F_VD) -> vs.VideoNode:
    _cached_clips = dict[str, vs.VideoNode]()

    def _eval_scale(f: vs.VideoFrame, n: int) -> vs.VideoNode:
        key = f'{f.width}_{f.height}'

        if key not in _cached_clips:
            const_clip = clip.resize.Point(f.width, f.height)

            _cached_clips[key] = function(const_clip)

        return _cached_clips[key]

    return clip.std.FrameEval(_eval_scale, clip, clip)
