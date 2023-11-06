from __future__ import annotations

from fractions import Fraction
from math import gcd as max_common_div
from typing import Callable, Iterable, Literal, NamedTuple, overload

import vapoursynth as vs
from stgpytools import Coordinate, CustomIntEnum, CustomStrEnum, Position, Sentinel, Size

from ..types import HoldsPropValueT

__all__ = [
    'Direction',
    'Dar', 'Sar',
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


class Dar(Fraction):
    @overload
    @staticmethod
    def from_size(width: int, height: int, sar: Sar | bool = True, /) -> Dar:
        ...

    @overload
    @staticmethod
    def from_size(clip: vs.VideoNode, sar: Sar | bool = True, /) -> Dar:
        ...

    @staticmethod
    def from_size(clip_width: vs.VideoNode | int, _height: int | Sar | bool = True, _sar: Sar | bool = True, /) -> Dar:
        width: int
        height: int
        sar: Sar | Literal[False]

        if isinstance(clip_width, vs.VideoNode):
            width, height, sar = clip_width.width, clip_width.height, _height  # type: ignore

            if sar is True:
                sar = Sar.from_clip(clip_width)  # type: ignore
        else:
            width, height, sar = clip_width, _height, _sar if isinstance(_sar, Sar) else False  # type: ignore

        gcd = max_common_div(width, height)

        if sar is False:
            sar = Sar(1, 1)

        return Dar(width // gcd * sar.numerator, height // gcd * sar.denominator)

    def to_sar(self, height: int, active_area: float) -> Sar:
        return Sar.from_dar(self, height, active_area)


class Sar(Fraction):
    @staticmethod
    def from_clip(clip: HoldsPropValueT) -> Sar:
        from ..utils import get_prop

        if isinstance(clip, vs.RawFrame):
            props = clip.props  # type: ignore
        elif isinstance(clip, vs.RawNode):
            props = clip.get_frame(0).props  # type: ignore
        else:
            props = clip

        return Sar(get_prop(props, '_SARNum', int, None, 1), get_prop(props, '_SARDen', int, None, 1))  # type: ignore

    @staticmethod
    def from_ar(den: int, num: int, height: int, active_area: float) -> Sar:
        return Dar(den, num).to_sar(height, active_area)

    @staticmethod
    def from_dar(dar: Dar, height: int, active_area: float) -> Sar:
        sar_n, sar_d = dar.numerator * height, dar.denominator * active_area

        if isinstance(active_area, float):
            sar_n, sar_d = int(sar_n * 10000), int(sar_d * 10000)

        gcd = max_common_div(sar_n, sar_d)

        return Sar(sar_n // gcd, sar_d // gcd)

    def apply(self, clip: vs.VideoNode) -> vs.VideoNode:
        return clip.std.SetFrameProps(_SARNum=self.numerator, _SARDen=self.denominator)


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
    def from_framerate(cls, framerate: float | Fraction, strict: bool = False) -> Region:
        """Determine the Region using a given framerate."""

        key = Fraction(framerate)

        if strict:
            return _framerate_region_map[key]

        if key not in _framerate_region_map:
            diffs = [(k, abs(float(key) - float(v))) for k, v in _region_framerate_map.items()]

            diffs.sort(key=lambda x: x[1])

            return diffs[0][0]

        return _framerate_region_map[key]


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

    def transpose(self) -> Resolution:
        return Resolution(self.height, self.width)

    def __str__(self) -> str:
        return f'{self.width}x{self.height}'


class SceneChangeMode(CustomIntEnum):
    """Enum for various scene change modes."""

    WWXD = 1
    SCXVID = 2
    WWXD_SCXVID_UNION = 3  # WWXD | SCXVID
    WWXD_SCXVID_INTERSECTION = 0  # WWXD & SCXVID

    @property
    def is_WWXD(self) -> bool:
        return self in (
            SceneChangeMode.WWXD, SceneChangeMode.WWXD_SCXVID_UNION,
            SceneChangeMode.WWXD_SCXVID_INTERSECTION
        )

    @property
    def is_SCXVID(self) -> bool:
        return self in (
            SceneChangeMode.SCXVID, SceneChangeMode.WWXD_SCXVID_UNION,
            SceneChangeMode.WWXD_SCXVID_INTERSECTION
        )

    def ensure_presence(self, clip: vs.VideoNode, akarin: bool | None = None) -> vs.VideoNode:
        from ..exceptions import CustomRuntimeError
        from ..utils import merge_clip_props

        stats_clip = []

        if self.is_SCXVID:
            if not hasattr(vs.core, 'scxvid'):
                raise CustomRuntimeError(
                    'You are missing scxvid!\n\tDownload it from https://github.com/dubhater/vapoursynth-scxvid',
                    self.ensure_presence
                )
            stats_clip.append(clip.scxvid.Scxvid())

        if self.is_WWXD:
            if not hasattr(vs.core, 'wwxd'):
                raise CustomRuntimeError(
                    'You are missing wwxd!\n\tDownload it from https://github.com/dubhater/vapoursynth-wwxd',
                    self.ensure_presence
                )
            stats_clip.append(clip.wwxd.WWXD())

        if akarin is None:
            akarin = hasattr(vs.core, 'akarin')

        if akarin:
            keys = list(self.prop_keys)

            expr = ' '.join([f'x.{k}' for k in keys]) + (' and' * (len(keys) - 1))

            blank = clip.std.BlankClip(1, 1, vs.GRAY8, keep=True)

            if len(stats_clip) > 1:
                return merge_clip_props(blank, *stats_clip).akarin.Expr(expr)

            return blank.std.CopyFrameProps(stats_clip[0]).akarin.Expr(expr)

        if len(stats_clip) > 1:
            return merge_clip_props(clip, *stats_clip)

        return stats_clip[0]

    @property
    def prop_keys(self) -> Iterable[str]:
        if self.is_WWXD:
            yield 'Scenechange'

        if self.is_SCXVID:
            yield '_SceneChangePrev'

    def check_cb(self, akarin: bool | None = None) -> Callable[[vs.VideoFrame], bool]:
        if akarin is None:
            akarin = hasattr(vs.core, 'akarin')

        if akarin:
            return (lambda f: bool(f[0][0, 0]))

        keys = set(self.prop_keys)
        prop_key = next(iter(keys))

        if self is SceneChangeMode.WWXD_SCXVID_UNION:
            return (lambda f: any(f.props[key] == 1 for key in keys))

        if self is SceneChangeMode.WWXD_SCXVID_INTERSECTION:
            return (lambda f: all(f.props[key] == 1 for key in keys))

        return (lambda f: f.props[prop_key] == 1)

    def lambda_cb(self, akarin: bool | None = None) -> Callable[[int, vs.VideoFrame], Sentinel.Type | int]:
        callback = self.check_cb(akarin)
        return (lambda n, f: Sentinel.check(n, callback(f)))

    def prepare_clip(self, clip: vs.VideoNode, height: int | None = 360, akarin: bool | None = None) -> vs.VideoNode:
        from ..utils import get_w

        if height is not None:
            clip = clip.resize.Bilinear(get_w(height, clip), height, vs.YUV420P8)
        elif not clip.format or (clip.format and clip.format.id != vs.YUV420P8):
            clip = clip.resize.Bilinear(format=vs.YUV420P8)

        return self.ensure_presence(clip, akarin)
