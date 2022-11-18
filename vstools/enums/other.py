from __future__ import annotations

from typing import NamedTuple

import vapoursynth as vs

from ..types import FuncExceptT
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
