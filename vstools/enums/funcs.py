from __future__ import annotations

from stgpytools import CustomStrEnum

__all__ = [
    'ConvMode'
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
