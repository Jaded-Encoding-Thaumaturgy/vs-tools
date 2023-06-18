from __future__ import annotations

from ..types import vs_object
from . import vs_proxy as vs
from typing import Generic, TypeVar

__all__ = [
    'ClipsCache',
    'FramesCache',
    'ClipFramesCache',

    'cache_clip'
]


NodeT = TypeVar('NodeT', bound=vs.RawNode)
FrameT = TypeVar('FrameT', bound=vs.RawFrame)


class ClipsCache(vs_object, dict[vs.VideoNode, vs.VideoNode]):
    def __delitem__(self, __key: vs.VideoNode) -> None:
        if __key not in self:
            return

        return super().__delitem__(__key)

    def __vs_del__(self, core_id: int) -> None:
        self.clear()


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

    def __getitem__(self, __key: int) -> FrameT:
        if __key not in self:
            self.add_frame(__key, self.clip.get_frame(__key))  # type: ignore

        return super().__getitem__(__key)

    def __vs_del__(self, core_id: int) -> None:
        self.clear()
        self.clip = None


class ClipFramesCache(vs_object, dict[vs.VideoNode, FramesCache[vs.VideoFrame]]):
    def _ensure_key(self, key: vs.VideoNode) -> None:
        if key not in self:
            super().__setitem__(key, FramesCache[vs.VideoFrame](key))

    def __setitem__(self, key: vs.VideoNode, value: FramesCache[vs.VideoFrame]) -> None:
        self._ensure_key(key)

        return super().__setitem__(key, value)

    def __getitem__(self, key: vs.VideoNode) -> FramesCache[vs.VideoFrame]:
        self._ensure_key(key)

        return super().__getitem__(key)

    def __vs_del__(self, core_id: int) -> None:
        self.clear()


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
