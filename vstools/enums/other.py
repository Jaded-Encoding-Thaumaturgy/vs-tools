from __future__ import annotations

from fractions import Fraction
from math import gcd as max_common_div
from typing import TYPE_CHECKING, Iterable, NamedTuple, TypeVar, overload

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
    'Size',
    'SceneChangeMode'
]


class Direction(CustomIntEnum):
    """Enum to simplify the direction argument."""

    HORIZONTAL = 0
    VERTICAL = 1

    LEFT = 2
    RIGHT = 3
    UP = 4
    DOWN = 5

    @property
    def is_axis(self) -> bool:
        """Whether the Direction represents an axis (horizontal/vertical)"""
        return self <= self.VERTICAL

    @property
    def is_way(self) -> bool:
        """Whether the Direction is one of the 4 arrow directions."""
        return self > self.VERTICAL

    @property
    def string(self) -> str:
        """A string representation of the Direction."""
        return self._name_.lower()


class Par(Fraction):
    @overload
    @staticmethod
    def get_ar(width: int, height: int, /) -> Fraction:
        """Calculate the aspect ratio using a given width and height."""

    @overload
    @staticmethod
    def get_ar(clip: vs.VideoNode, /) -> Fraction:
        """Calculate the aspect ratio using a given clip's width and height."""

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
    FULL = 'full'
    SQUARE = 'square'

    @classmethod
    def from_video(
        cls, src: vs.VideoNode | vs.VideoFrame | vs.FrameProps, strict: bool = False, func: FuncExceptT | None = None
    ) -> Dar:
        """Calculate the Dar using a given clip's frame properties."""

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
    """Unknown region."""

    NTSC = 'NTSC'
    """
    The first American standard for analog television broadcast was developed by
    National Television System Committee (NTSC) in 1941.

    For more information see `this <https://en.wikipedia.org/wiki/NTSC>`_.
    """

    NTSCi = 'NTSCi'
    """Interlaced NTSC."""

    PAL = 'PAL'
    """
    Phase Alternating Line (PAL) colour encoding system.

    For more information see `this <https://en.wikipedia.org/wiki/PAL>`_.
    """

    PALi = 'PALi'
    """Interlaced PAL."""

    FILM = 'FILM'
    """True 24fps content."""

    NTSC_FILM = 'NTSC (FILM)'
    """NTSC 23.976fps content."""

    @property
    def framerate(self) -> Fraction:
        """Obtain the Region's framerate."""
        return _region_framerate_map[self]

    @classmethod
    def from_framerate(cls, framerate: float | Fraction) -> Region:
        """Determine the Region using a given framerate."""
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
    height: int

    @classmethod
    def from_video(cls, clip: vs.VideoNode) -> Resolution:
        from ..functions import check_variable_resolution

        assert check_variable_resolution(clip, cls.from_video)

        return Resolution(clip.width, clip.height)

    def __str__(self) -> str:
        return f'{self.width}x{self.height}'


class Coordinate:
    """
    Positive set of (x, y) coordinates.

    :raises ValueError:     Negative values were passed.
    """

    x: int
    """Horizontal coordinate."""

    y: int
    """Vertical coordinate."""

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
    """Positive set of an (x,y) offset relative to the top left corner of the image."""


class Size(Coordinate):
    """Positive set of an (x,y), (horizontal,vertical), size of the image."""


class SceneChangeMode(CustomIntEnum):
    """Enum for various scene change modes."""

    WWXD = 1
    SCXVID = 2

    if not TYPE_CHECKING:
        WWXD_SCXVID_UNION = 3  # WWXD | SCXVID
        WWXD_SCXVID_INTERSECTION = 0  # WWXD & SCXVID

    @property
    def is_WWXD(self) -> bool:
        return self in (
            SceneChangeMode.WWXD, SceneChangeMode.WWXD_SCXVID_UNION,   # type: ignore
            SceneChangeMode.WWXD_SCXVID_INTERSECTION   # type: ignore
        )

    @property
    def is_SCXVID(self) -> bool:
        return self in (
            SceneChangeMode.SCXVID, SceneChangeMode.WWXD_SCXVID_UNION,  # type: ignore
            SceneChangeMode.WWXD_SCXVID_INTERSECTION  # type: ignore
        )

    def ensure_presence(self, clip: vs.VideoNode) -> vs.VideoNode:
        if self.is_WWXD:
            clip = clip.wwxd.WWXD()

        if self.is_SCXVID:
            clip = clip.scxvid.Scxvid()

        return clip

    @property
    def prop_keys(self) -> Iterable[str]:
        if self.is_WWXD:
            yield 'Scenechange'

        if self.is_SCXVID:
            yield '_SceneChangePrev'
