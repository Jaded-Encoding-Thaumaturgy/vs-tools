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
    """
    Shift a clip forwards or backwards by *n* frames.

    This is useful for cases where you must compare every frame of a clip
    with the frame that comes before or after the current frame,
    like for example when performing termporal operations.

    Both positive and negative integers are allowed.
    Positive values will shift a clip forward, negative will shift a clip backward.

    :param clip:            Input clip.
    :param offset:          Number of frames to offset the clip with. Negative values are allowed.
                            Positive values will shift a clip forward,
                            negative will shift a clip backward.

    :returns:               Clip that has been shifted forwards or backwards by *n* frames.
    """
    if offset > clip.num_frames - 1:
        raise FramesLengthError(shift_clip, 'offset')

    if offset < 0:
        return clip[0] * abs(offset) + clip[:offset]

    if offset > 0:
        return clip[offset:] + clip[-1] * offset

    return clip


def shift_clip_multi(clip: vs.VideoNode, offsets: FrameRange = (-1, 1)) -> list[vs.VideoNode]:
    """
    Shift a clip forwards or backwards multiple times by a varying amount of frames.

    This will return a clip for every shifting operation performed.
    This is a convenience function that should make handling multiple shifts a lot easier.


    Example:
    .. code-block:: python
        >>> shift_clip_multi(clip, (-3, 3))
            -3         -2         -1          0         +1         +2         +3
        [VideoNode, VideoNode, VideoNode, VideoNode, VideoNode, VideoNode, VideoNode]

    :param clip:            Input clip.
    :param offsets:         List of frame ranges for offsetting.
                            A clip will be returned for every offset.
                            Default: (-1, 1).

    :return:                A list of clips, the amount determined by the amount of offsets.
    """
    ranges = normalize_franges(offsets)

    return [shift_clip(clip, x) for x in ranges]


def process_var_clip(clip: vs.VideoNode, function: F_VD) -> vs.VideoNode:
    """
    Process variable format/resolution clips with a given function.

    This function will temporarily assert a resolution and format for a variable clip,
    run the given function, and then return a variable format clip back.

    The function must accept a VideoNode and return a VideoNode.

    :param clip:        Input clip.
    :param function:    Function that takes and returns a single VideoNode.

    :return:            Processed variable clip.
    """

    _cached_clips = dict[str, vs.VideoNode]()

    def _eval_scale(f: vs.VideoFrame, n: int) -> vs.VideoNode:
        key = f'{f.width}_{f.height}'

        if key not in _cached_clips:
            const_clip = clip.resize.Point(f.width, f.height)

            _cached_clips[key] = function(const_clip)

        return _cached_clips[key]

    return clip.std.FrameEval(_eval_scale, clip, clip)
