from __future__ import annotations

from stgpytools import CustomStrEnum, CustomIntEnum

__all__ = [
    'ConvMode',

    'BaseAlign', 'Align'
]


class ConvMode(CustomStrEnum):
    """Convolution mode for .std.Convolution."""

    SQUARE = 's'
    """Square horizontal/vertical convolution."""

    VERTICAL = 'v'
    """Vertical-only convolution."""

    HORIZONTAL = 'h'
    """Horizontal-only convolution."""

    HV = 'hv'
    """Horizontal and Vertical convolution"""

    TEMPORAL = "t"
    """Temporal convolution"""

class BaseAlign(CustomIntEnum):
    TOP = 1
    MIDDLE = 2
    BOTTOM = 4
    LEFT = 8
    CENTER = 16
    RIGHT = 32


class Align(CustomIntEnum):
    TOP_LEFT = BaseAlign.TOP | BaseAlign.LEFT
    TOP_CENTER = BaseAlign.TOP | BaseAlign.CENTER
    TOP_RIGHT = BaseAlign.TOP | BaseAlign.RIGHT
    MIDDLE_LEFT = BaseAlign.MIDDLE | BaseAlign.LEFT
    MIDDLE_CENTER = BaseAlign.MIDDLE | BaseAlign.CENTER
    MIDDLE_RIGHT = BaseAlign.MIDDLE | BaseAlign.RIGHT
    BOTTOM_LEFT = BaseAlign.BOTTOM | BaseAlign.LEFT
    BOTTOM_CENTER = BaseAlign.BOTTOM | BaseAlign.CENTER
    BOTTOM_RIGHT = BaseAlign.BOTTOM | BaseAlign.RIGHT
