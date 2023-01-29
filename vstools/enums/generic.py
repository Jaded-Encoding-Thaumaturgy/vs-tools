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
    """Chroma sample position in YUV formats."""

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
    def from_video(
        cls, src: vs.VideoNode | vs.VideoFrame | vs.FrameProps, strict: bool = False, func: FuncExceptT | None = None
    ) -> ChromaLocation:
        """
        Obtain the chroma location of a clip from the frame properties.

        :param src:                             Input clip, frame, or props.
        :param strict:                          Be strict about the properties.
                                                The result may NOT be an unknown value.

        :return:                                ChromaLocation object.

        :raises UndefinedChromaLocationError:   Chroma location is undefined.
        :raises UndefinedChromaLocationError:   Chroma location can not be determined from the frame properties.
        """

        return _base_from_video(cls, src, UndefinedChromaLocationError, strict, func)

    @classmethod
    def get_offsets(
        cls, chroma_loc: ChromaLocation | vs.VideoNode
    ) -> tuple[float, float]:
        """Get (left,top) shift for chroma relative to luma."""

        if isinstance(chroma_loc, vs.VideoNode):
            assert chroma_loc.format  # type: ignore
            subsampling = (chroma_loc.format.subsampling_w, chroma_loc.format.subsampling_h)  # type: ignore

            if subsampling in [(1, 0), (1, 1)]:
                offsets = (0.5, 0)
            elif subsampling == (0, 1):
                offsets = (0, 0)
            elif subsampling == (2, 0):
                offsets = (2.5, 0)
            elif subsampling == (2, 2):
                offsets = (2.5, 1)

            return offsets

        off_left = off_top = 0.0

        if chroma_loc in {ChromaLocation.LEFT, ChromaLocation.TOP_LEFT, ChromaLocation.BOTTOM_LEFT}:
            off_left += -0.5

        if chroma_loc in {ChromaLocation.TOP, ChromaLocation.TOP_LEFT}:
            off_top += -0.5
        elif chroma_loc in {ChromaLocation.BOTTOM, ChromaLocation.BOTTOM_LEFT}:
            off_top += +0.5

        return off_left, off_top


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
    """The frame is progressive."""

    BFF = 1
    """The frame is interlaced and the field order is bottom field first."""

    TFF = 2
    """The frame is interlaced and the field order is top field first."""

    if not TYPE_CHECKING:
        @classmethod
        def from_param(cls: Any, value_or_tff: Any, func_except: Any = None) -> FieldBased | None:
            if isinstance(value_or_tff, bool):
                return FieldBased(1 + value_or_tff)

            return super().from_param(value_or_tff)

    @classmethod
    def from_res(cls, frame: vs.VideoNode | vs.VideoFrame) -> FieldBased:
        """Guess the Field order from the frame resolution."""

        return cls.PROGRESSIVE

    @classmethod
    def from_video(
        cls, src: vs.VideoNode | vs.VideoFrame | vs.FrameProps, strict: bool = False, func: FuncExceptT | None = None
    ) -> FieldBased:
        """
        Obtain the Field order of a clip from the frame properties.

        :param src:                             Input clip, frame, or props.
        :param strict:                          Be strict about the properties.
                                                The result may NOT be an unknown value.

        :return:                                FieldBased object.

        :raises UndefinedFieldBasedError:       Field order is undefined.
        :raises UndefinedFieldBasedError:       Field order can not be determined from the frame properties.
        """

        return _base_from_video(cls, src, UndefinedFieldBasedError, strict, func)

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

    @property
    def pretty_string(self) -> str:
        if self.is_inter:
            return f"{'Top' if self.is_tff else 'Bottom'} Field First"

        return super().pretty_string


ChromaLocationT: TypeAlias = Union[int, vs.ChromaLocation, ChromaLocation]
"""Type alias for values that can be used to initialize a :py:attr:`ChromaLocation`."""

FieldBasedT: TypeAlias = Union[int, vs.FieldBased, FieldBased]
"""Type alias for values that can be used to initialize a :py:attr:`FieldBased`."""
