from __future__ import annotations

from ..types import vs_object
from . import vs_proxy as vs
from typing import Generic, TypeVar

__all__ = [
    'FramesCache',

    'cache_clip'
]


NodeT = TypeVar('NodeT', bound=vs.RawNode)
FrameT = TypeVar('FrameT', bound=vs.RawFrame)


class FramesCache(vs_object, Generic[FrameT], dict[int, FrameT]):
    def __init__(self, clip: vs.VideoNode, cache_size: int = 10) -> None:
        self.clip = clip
        self.cache_size = cache_size

    def add_frame(self, n: int, f: FrameT) -> FrameT:
        self[n] = f.copy()
        return self[n]

    def get_frame(self, n: int, f: FrameT) -> FrameT:
        return self[n]

    def __setitem__(self, __key: int, __value: FrameT) -> None:
        super().__setitem__(__key, __value)

        if self.cache_size < len(self):
            del self[next(iter(self.keys()))]

    def __vs_del__(self, core_id: int) -> None:
        self.clear()
        del self.clip


def cache_clip(_clip: NodeT, cache_size: int = 10) -> NodeT:
    if isinstance(_clip, vs.VideoNode):
        clip: vs.VideoNode = _clip  # type: ignore

        cache = FramesCache[vs.VideoFrame](clip, cache_size)

        blank = clip.std.BlankClip()

        _to_cache_node = blank.std.ModifyFrame(clip, cache.add_frame)
        _from_cache_node = blank.std.ModifyFrame(blank, cache.get_frame)

        return blank.std.FrameEval(  # type: ignore
            lambda n: _from_cache_node if n in cache else _to_cache_node
        )
    # elif isinstance(_clip, vs.AudioNode):
    #     ...

    return _clip
