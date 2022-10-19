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
    """@@PLACEHOLDER@@"""

    VERTICAL = 1
    """@@PLACEHOLDER@@"""


class Dar(CustomStrEnum):
    """StrEnum signifying an analog television aspect ratio."""

    WIDE = WIDESCREEN = 'widescreen'
    """@@PLACEHOLDER@@"""

    FULL = FULLSCREEN = 'fullscreen'
    """@@PLACEHOLDER@@"""

    SQUARE = 'square'
    """@@PLACEHOLDER@@"""


class Region(CustomStrEnum):
    """StrEnum signifying an analog television region."""

    NTSC = 'NTSC'
    """@@PLACEHOLDER@@"""

    NTSCJ = 'NTSCJ'
    """@@PLACEHOLDER@@"""

    PAL = 'PAL'
    """@@PLACEHOLDER@@"""


class Resolution(NamedTuple):
    """Tuple representing a resolution."""

    width: int
    """@@PLACEHOLDER@@"""

    height: int
    """@@PLACEHOLDER@@"""
