from __future__ import annotations

from .base import CustomStrEnum

__all__ = [
    'ConvMode'
]


class ConvMode(CustomStrEnum):
    """Convolution mode for .std.Convolution."""

    SQUARE = 'hv'
    """Square horizontal/vertical convolution."""

    VERTICAL = 'v'
    """Vertical only convolution."""

    HORIZONTAL = 'h'
    """Horizontal only convolution."""
