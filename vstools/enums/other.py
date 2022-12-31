from __future__ import annotations

from fractions import Fraction
from math import gcd as max_common_div
from typing import NamedTuple, TypeVar, overload

import vapoursynth as vs

from ..types import FuncExceptT
from .base import CustomIntEnum, CustomStrEnum

__all__ = [
    'Direction',
    'Dar', 'Par',
    'Region',
    'Resolution',
    'Coordinate',
    'Position',
    'Size'
]


class Direction(CustomIntEnum):
    """Enum to simplify direction argument."""

    HORIZONTAL = 0
    """@@PLACEHOLDER@@"""

    VERTICAL = 1
    """@@PLACEHOLDER@@"""

    LEFT = 2
    RIGHT = 3
    UP = 4
    DOWN = 5

    @property
    def is_axis(self) -> bool:
        """@@PLACEHOLDER@@"""
        return self <= self.VERTICAL

    @property
    def is_way(self) -> bool:
        """@@PLACEHOLDER@@"""
        return self > self.VERTICAL

    @property
    def string(self) -> str:
        """@@PLACEHOLDER@@"""
        return self._name_.lower()


class Par(Fraction):
    @overload
    @staticmethod
    def get_ar(width: int, height: int, /) -> Fraction:
        """@@PLACEHOLDER@@"""

    @overload
    @staticmethod
    def get_ar(clip: vs.VideoNode, /) -> Fraction:
        """@@PLACEHOLDER@@"""

    @staticmethod
    def get_ar(clip_width: vs.VideoNode | int, height: int = 0, /) -> Fraction:
        if isinstance(clip_width, vs.VideoNode):
            width, height = clip_width.width, clip_width.height  # type: ignore
        else:
            width, height = clip_width, height

        gcd = max_common_div(width, height)

        return Fraction(int(width / gcd), int(height / gcd))


class Dar(CustomStrEnum):
    """StrEnum signifying an analog television aspect ratio."""

    WIDE = 'wide'
    """@@PLACEHOLDER@@"""

    FULL = 'full'
    """@@PLACEHOLDER@@"""

    SQUARE = 'square'
    """@@PLACEHOLDER@@"""

    @classmethod
    def from_video(
        cls, src: vs.VideoNode | vs.VideoFrame | vs.FrameProps, strict: bool = False, func: FuncExceptT | None = None
    ) -> Dar:
        """@@PLACEHOLDER@@"""

        from ..exceptions import CustomValueError, FramePropError
        from ..utils import get_prop

        try:
            sar = get_prop(src, "_SARDen", int), get_prop(src, "_SARNum", int)
        except FramePropError:
            if strict:
                raise FramePropError(
                    '', '', 'SAR props not found! Make sure your video indexing plugin sets them!'
                )

            return Dar.WIDE

        match sar:
            case (11, 10) | (9, 8): return Dar.FULL
            case (33, 40) | (27, 32): return Dar.WIDE

        raise CustomValueError("Could not calculate DAR. Please set the DAR manually.")


class Region(CustomStrEnum):
    """StrEnum signifying an analog television region."""

    UNKNOWN = 'unknown'
    """@@PLACEHOLDER@@"""

    NTSC = 'NTSC'
    """@@PLACEHOLDER@@"""

    NTSCi = 'NTSCi'
    """@@PLACEHOLDER@@"""

    PAL = 'PAL'
    """@@PLACEHOLDER@@"""

    PALi = 'PALi'
    """@@PLACEHOLDER@@"""

    FILM = 'FILM'
    """@@PLACEHOLDER@@"""

    NTSC_FILM = 'NTSC (FILM)'
    """@@PLACEHOLDER@@"""

    @property
    def framerate(self) -> Fraction:
        """@@PLACEHOLDER@@"""
        return _region_framerate_map[self]

    @classmethod
    def from_framerate(cls, framerate: float | Fraction) -> Region:
        """@@PLACEHOLDER@@"""
        return _framerate_region_map[Fraction(framerate)]


_region_framerate_map = {
    Region.UNKNOWN: Fraction(0),
    Region.NTSC: Fraction(30000, 1001),
    Region.NTSCi: Fraction(60000, 1001),
    Region.PAL: Fraction(25, 1),
    Region.PALi: Fraction(50, 1),
    Region.FILM: Fraction(24, 1),
    Region.NTSC_FILM: Fraction(24000, 1001),
}

_framerate_region_map = {r.framerate: r for r in Region}


class Resolution(NamedTuple):
    """Tuple representing a resolution."""

    width: int
    """@@PLACEHOLDER@@"""

    height: int
    """@@PLACEHOLDER@@"""


class Coordinate:
    """
    Positive set of (x, y) coordinates.

    :raises ValueError:     Negative values get passed.
    """

    x: int
    """@@PLACEHOLDER@@"""

    y: int
    """@@PLACEHOLDER@@"""

    @overload
    def __init__(self: SelfCoord, other: tuple[int, int] | SelfCoord, /) -> None:
        ...

    @overload
    def __init__(self: SelfCoord, x: int, y: int, /) -> None:
        ...

    def __init__(self: SelfCoord, x_or_self: int | tuple[int, int] | SelfCoord, y: int, /) -> None:  # type: ignore
        from ..exceptions import CustomValueError

        if isinstance(x_or_self, int):
            x = x_or_self
        else:
            x, y = x_or_self if isinstance(x_or_self, tuple) else (x_or_self.x, x_or_self.y)

        if x < 0 or y < 0:
            raise CustomValueError("Values can't be negative!", self.__class__)

        self.x = x
        self.y = y


SelfCoord = TypeVar('SelfCoord', bound=Coordinate)


class Position(Coordinate):
    """@@PLACEHOLDER@@"""


class Size(Coordinate):
    """@@PLACEHOLDER@@"""
