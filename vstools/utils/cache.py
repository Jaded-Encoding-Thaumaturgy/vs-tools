from __future__ import annotations

from typing import Any, Generic, TypeVar

from stgpytools import T

from ..functions import Keyframes
from ..types import vs_object
from . import vs_proxy as vs

__all__ = [
    'ClipsCache',

    'DynamicClipsCache',

    'FramesCache',

    'ClipFramesCache',

    'SceneBasedDynamicCache',

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


class DynamicClipsCache(vs_object, dict[T, vs.VideoNode]):
    def __init__(self, cache_size: int = 2) -> None:
        self.cache_size = cache_size

    def get_clip(self, key: T) -> vs.VideoNode:
        raise NotImplementedError

    def __getitem__(self, __key: T) -> vs.VideoNode:
        if __key not in self:
            self[__key] = self.get_clip(__key)

            if len(self) > self.cache_size:
                del self[next(iter(self.keys()))]

        return super().__getitem__(__key)


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

        if len(self) > self.cache_size:
            del self[next(iter(self.keys()))]

    def __getitem__(self, __key: int) -> FrameT:
        if __key not in self:
            self.add_frame(__key, self.clip.get_frame(__key))  # type: ignore

        return super().__getitem__(__key)

    def __vs_del__(self, core_id: int) -> None:
        self.clear()
        self.clip = None  # type: ignore


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


class SceneBasedDynamicCache(DynamicClipsCache[int]):
    def __init__(self, clip: vs.VideoNode, keyframes: Keyframes | str, cache_size: int = 5) -> None:
        super().__init__(cache_size)

        self.clip = clip
        self.keyframes = Keyframes.from_param(clip, keyframes)

    def get_clip(self, key: int) -> vs.VideoNode:
        raise NotImplementedError

    def get_eval(self) -> vs.VideoNode:
        return self.clip.std.FrameEval(lambda n: self[self.keyframes.scenes.indices[n]])

    @classmethod
    def from_clip(cls, clip: vs.VideoNode, keyframes: Keyframes | str, *args: Any, **kwargs: Any) -> vs.VideoNode:
        return cls(clip, keyframes, *args, **kwargs).get_eval()


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
