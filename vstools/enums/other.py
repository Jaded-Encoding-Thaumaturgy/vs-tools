from __future__ import annotations

from typing import NamedTuple

from .base import CustomIntEnum, CustomStrEnum

__all__ = [
    'Direction',
    'Dar',
    'Region',
    'Resolution'
]


class Direction(CustomIntEnum):
    """Enum to simplify direction argument."""

    HORIZONTAL = 0
    VERTICAL = 1


class Dar(CustomStrEnum):
    """StrEnum signifying an analog television aspect ratio."""

    WIDE = WIDESCREEN = 'widescreen'
    FULL = FULLSCREEN = 'fullscreen'
    SQUARE = 'square'


class Region(CustomStrEnum):
    """StrEnum signifying an analog television region."""

    NTSC = 'NTSC'
    NTSCJ = 'NTSCJ'
    PAL = 'PAL'


class Resolution(NamedTuple):
    """Tuple representing a resolution."""

    width: int

    height: int
