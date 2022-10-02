from __future__ import annotations

from .base import CustomStrEnum

__all__ = [
    'ConvMode'
]


class ConvMode(CustomStrEnum):
    SQUARE = 'hv'
    VERTICAL = 'v'
    HORIZONTAL = 'h'
