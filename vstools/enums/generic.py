from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeAlias, Union

import vapoursynth as vs

from ..exceptions import (
    UndefinedChromaLocationError, UndefinedFieldBasedError, UnsupportedChromaLocationError, UnsupportedFieldBasedError
)
from ..types import FuncExceptT
from .stubs import _base_from_video, _ChromaLocationMeta, _FieldBasedMeta

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

    @classmethod
    def from_res(cls, frame: vs.VideoNode | vs.VideoFrame) -> ChromaLocation:
        from ..utils import get_var_infos

        _, width, _ = get_var_infos(frame)

        if width >= 3840:
            return ChromaLocation.TOP_LEFT

        return ChromaLocation.LEFT

    @classmethod
    def from_video(
        cls, src: vs.VideoNode | vs.VideoFrame | vs.FrameProps, strict: bool = False, func: FuncExceptT | None = None
    ) -> ChromaLocation:
        return _base_from_video(cls, src, UndefinedChromaLocationError, strict, func)


class FieldBased(_FieldBasedMeta):
    """Whether the frame is composed of two independent fields (interlaced) and their order."""

    _value_: int

    @classmethod
    def _missing_(cls: type[FieldBased], value: Any) -> FieldBased | None:
        value = super()._missing_(value)

        if value is None:
            return cls.PROGRESSIVE

        if value > cls.TFF:
            raise UnsupportedFieldBasedError(f'FieldBased({value}) is unsupported.', cls)

        return None

    PROGRESSIVE = 0
    BFF = 1
    TFF = 2

    if not TYPE_CHECKING:
        @classmethod
        def from_param(cls: Any, value_or_tff: Any, func_except: Any = None) -> FieldBased | None:
            if isinstance(value_or_tff, bool):
                return FieldBased(1 + value_or_tff)

            return super().from_param(value_or_tff)

    @classmethod
    def from_res(cls, frame: vs.VideoNode | vs.VideoFrame) -> FieldBased:
        return cls.PROGRESSIVE

    @classmethod
    def from_video(
        cls, src: vs.VideoNode | vs.VideoFrame | vs.FrameProps, strict: bool = False, func: FuncExceptT | None = None
    ) -> FieldBased:
        return _base_from_video(cls, src, UndefinedFieldBasedError, strict, func)

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

    @property
    def pretty_string(self) -> str:
        if self.is_inter:
            return f"{'Top' if self.is_tff else 'Bottom'} Field First" 

        return super().pretty_string

ChromaLocationT: TypeAlias = Union[int, vs.ChromaLocation, ChromaLocation]
FieldBasedT: TypeAlias = Union[int, vs.FieldBased, FieldBased]
