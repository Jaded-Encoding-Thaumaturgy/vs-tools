from __future__ import annotations

from typing import TYPE_CHECKING, Any

import vapoursynth as vs

from ..exceptions import (
    UndefinedChromaLocationError, UndefinedFieldBasedError, UnsupportedChromaLocationError, UnsupportedFieldBasedError
)
from ..types import MISSING, FuncExceptT
from .stubs import _ChromaLocationMeta, _FieldBasedMeta

__all__ = [
    'ChromaLocation', 'ChromaLocationT',

    'FieldBased', 'FieldBasedT'
]


class ChromaLocation(_ChromaLocationMeta):
    """Chroma sample position in YUV formats"""

    _value_: int

    @classmethod
    def _missing_(cls: type[ChromaLocation], value: Any) -> ChromaLocation | None:
        if value is None:
            return cls.LEFT

        if value > cls.BOTTOM:
            raise UnsupportedChromaLocationError(f'ChromaLocation({value}) is unsupported.', cls)

        return None

    LEFT = 0
    CENTER = 1
    TOP_LEFT = 2
    TOP = 3
    BOTTOM_LEFT = 4
    BOTTOM = 5

    @property
    def is_unknown(self) -> bool:
        return False

    @classmethod
    def from_res(cls, frame: vs.VideoNode | vs.VideoFrame) -> ChromaLocation:
        from ..utils import get_var_infos

        _, width, _ = get_var_infos(frame)

        if width >= 3840:
            return ChromaLocation.TOP_LEFT

        return ChromaLocation.LEFT

    @classmethod
    def from_video(cls, src: vs.VideoNode | vs.VideoFrame | vs.FrameProps, strict: bool = False) -> ChromaLocation:
        from ..utils import get_prop

        value = get_prop(src, '_ChromaLocation', int, default=MISSING if strict else None)

        if value is None:
            if strict:
                raise UndefinedChromaLocationError(f'ChromaLocation({value}) is undefined.', cls.from_video)

            if isinstance(src, vs.FrameProps):
                raise UndefinedChromaLocationError('Can\'t determine chroma location from FrameProps.', cls.from_video)

            return cls.from_res(src)

        return cls(value)


class FieldBased(_FieldBasedMeta):
    """Whether the frame is composed of two independent fields (interlaced) and their order."""

    _value_: int

    @classmethod
    def _missing_(cls: type[FieldBased], value: Any) -> FieldBased | None:
        if value is None:
            return cls.PROGRESSIVE

        if value > cls.TFF:
            raise UnsupportedFieldBasedError(f'FieldBased({value}) is unsupported.', cls)

        return None

    PROGRESSIVE = 0
    BFF = 1
    TFF = 2

    @property
    def is_unknown(self) -> bool:
        return False

    if not TYPE_CHECKING:
        @classmethod
        def from_param(cls: Any, value_or_tff: Any, func_except: Any = None) -> FieldBased | None:
            if isinstance(value_or_tff, bool):
                return FieldBased(1 + value_or_tff)

            return super().from_param(value_or_tff)

    @classmethod
    def from_video(cls, src: vs.VideoNode | vs.VideoFrame | vs.FrameProps, strict: bool = False) -> FieldBased:
        from ..utils import get_prop

        value = get_prop(src, '_FieldBased', int, default=MISSING if strict else None)

        if value is None:
            if strict:
                raise UndefinedFieldBasedError(f'FieldBased({value}) is undefined.', cls.from_video)

            if isinstance(src, vs.FrameProps):
                raise UndefinedFieldBasedError('Can\'t determine field type from FrameProps.', cls.from_video)

            return FieldBased.PROGRESSIVE

        return cls(value)

    @property
    def is_inter(self) -> bool:
        return self != FieldBased.PROGRESSIVE

    @property
    def field(self) -> int:
        if self.PROGRESSIVE:
            raise UnsupportedFieldBasedError(
                'Progressive video aren\'t field based!',
                f'{self.__class__.__name__}.field'
            )

        return self.value - 1

    @property
    def is_tff(self) -> bool:
        return self is self.TFF

    @classmethod
    def ensure_presence(
        cls, clip: vs.VideoNode,
        tff: bool | int | FieldBased | None,
        func: FuncExceptT | None = None
    ) -> vs.VideoNode:
        value = FieldBased.from_param(tff, func) or FieldBased.from_video(clip, True)

        return clip.std.SetFieldBased(value.field)


ChromaLocationT = int | vs.ChromaLocation | ChromaLocation
FieldBasedT = int | vs.FieldBased | FieldBased
