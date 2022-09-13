from __future__ import annotations

from typing import TYPE_CHECKING, Any

import vapoursynth as vs

from ..exceptions import (
    UndefinedChromaLocationError, UndefinedFieldBasedError, UnsupportedChromaLocationError, UnsupportedFieldBasedError
)
from ..types import MISSING
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
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    CENTER = 1
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    TOP_LEFT = 2
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    TOP = 3
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    BOTTOM_LEFT = 4
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    BOTTOM = 5
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""

    @property
    def is_unknown(self) -> bool:
        return False

    @classmethod
    def from_res(cls, frame: vs.VideoNode | vs.VideoFrame) -> ChromaLocation:
        """
        Guess the chroma location based on the clip's resolution.

        :param frame:       Input clip or frame.

        :return:            ChromaLocation object.
        """
        from ..utils import get_var_infos

        _, width, _ = get_var_infos(frame)

        if width >= 3840:
            return ChromaLocation.TOP_LEFT

        return ChromaLocation.LEFT

    @classmethod
    def from_video(cls, src: vs.VideoNode | vs.VideoFrame | vs.FrameProps, strict: bool = False) -> ChromaLocation:
        """
        Obtain the chroma location of a clip from the frame properties.

        :param src:                             Input clip, frame, or props.
        :param strict:                          Be strict about the properties.
                                                The result may NOT be an unknown value.

        :return:                                ChromaLocation object.

        :raises UndefinedChromaLocationError:   Chroma location is undefined.
        :raises UndefinedChromaLocationError:   Chroma location can not be determined from the frameprops.
        """
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
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    BFF = 1
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    TFF = 2
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""

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
        """
        Obtain the Field order of a clip from the frame properties.

        :param src:                             Input clip, frame, or props.
        :param strict:                          Be strict about the properties.
                                                The result may NOT be an unknown value.

        :return:                                FieldBased object.

        :raises UndefinedFieldBasedError:       Field order is undefined.
        :raises UndefinedFieldBasedError:       Field order can not be determined from the frameprops.
        """
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
        """Check whether the value belongs to an interlaced value."""
        return self != FieldBased.PROGRESSIVE

    @property
    def field(self) -> int:
        """
        Check what field the enum signifies.

        :raises UnsupportedFieldBasedError:      PROGRESSIVE value is passed.
        """
        if self.PROGRESSIVE:
            raise UnsupportedFieldBasedError(
                'Progressive video aren\'t field based!',
                f'{self.__class__.__name__}.field'
            )

        return self.value - 1

    @property
    def is_tff(self) -> bool:
        """Check whether the value is Top-Field-First."""
        return self is self.TFF


ChromaLocationT = int | vs.ChromaLocation | ChromaLocation
"""@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""

FieldBasedT = int | vs.FieldBased | FieldBased
"""@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
