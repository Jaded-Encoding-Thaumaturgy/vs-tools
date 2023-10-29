from __future__ import annotations

from typing import Iterable, Sequence

import vapoursynth as vs
from stgpytools import FuncExceptT, T, cachedproperty, fallback, iterate, kwargs_fallback, normalize_seq, to_arr

from ..enums import ColorRange, ColorRangeT, Matrix, MatrixT
from ..exceptions import InvalidColorFamilyError
from ..types import ConstantFormatVideoNode, HoldsVideoFormatT, PlanesT, VideoFormatT
from .check import check_variable
from .normalize import normalize_planes
from .utils import depth, join, plane

__all__ = [
    'iterate', 'fallback', 'kwargs_fallback',

    'FunctionUtil'
]


class FunctionUtil(cachedproperty.baseclass, list[int]):
    """
    Function util to normalize common actions and boilerplate often used in functions.

    Main use is:
        - Automatically convert to OPP if input is RGB and function only supports GRAY, YUV.
        - Automatically dither up and down as the function needs.
        - Handle the variable clip check.
        - Fully type safe and remove the need for asserts or typeguards in function code.
        - Handy properties for common code paths, and improve code readability.
    """

    def __init__(
        self, clip: vs.VideoNode, func: FuncExceptT, planes: PlanesT = None,
        color_family: VideoFormatT | HoldsVideoFormatT | vs.ColorFamily | Iterable[
            VideoFormatT | HoldsVideoFormatT | vs.ColorFamily
        ] | None = None, bitdepth: int | range | tuple[int, int] | None = None, strict: bool = False,
        *, matrix: MatrixT | None = None, range_in: ColorRangeT | None = None
    ) -> None:
        from ..utils import get_color_family

        assert check_variable(clip, func)

        if color_family is not None:
            color_family = [get_color_family(c) for c in to_arr(color_family)]  # type: ignore

            if strict:
                InvalidColorFamilyError.check(clip, color_family, func)

        if isinstance(bitdepth, tuple):
            bitdepth = range(*bitdepth)

        self.clip = clip
        self.planes = planes
        self.func = func
        self.strict = strict
        self.allowed_cfamilies = color_family
        self.cfamily_converted = False
        self.bitdepth = bitdepth

        self._matrix = matrix
        self._range_in = range_in

        self.norm_planes = normalize_planes(self.norm_clip, planes)

        super().__init__(self.norm_planes)

        self.num_planes = self.work_clip.format.num_planes

    @cachedproperty
    def norm_clip(self) -> ConstantFormatVideoNode:
        """Get a "normalized" clip. This means color space, and bitdepth conversion if needed."""

        if isinstance(self.bitdepth, range) and self.clip.format.bits_per_sample not in self.bitdepth:
            clip = depth(self.clip, self.bitdepth.stop)
        elif isinstance(self.bitdepth, int):
            clip = depth(self.clip, self.bitdepth)
        else:
            clip = self.clip

        assert clip.format

        cfamily = clip.format.color_family

        if self.allowed_cfamilies and cfamily not in self.allowed_cfamilies:
            if cfamily is vs.RGB:
                from ..utils import Colorspace

                clip = Colorspace.OPP(clip)

                self.cfamily_converted = True

            if cfamily is vs.YUV and vs.GRAY in self.allowed_cfamilies:
                clip = plane(clip, 0)

        return clip  # type: ignore

    @cachedproperty
    def work_clip(self) -> ConstantFormatVideoNode:
        """Get the "work clip" as specified from the input planes."""

        return plane(self.norm_clip, 0) if self.luma_only else self.norm_clip  # type: ignore

    @cachedproperty
    def chroma_planes(self) -> list[vs.VideoNode]:
        """Get chroma planes if possible."""

        if self != [0] or self.norm_clip.format.num_planes == 1:
            return []
        return [plane(self.norm_clip, i) for i in {1, 2}]

    @cachedproperty
    def matrix(self) -> Matrix:
        return (
            Matrix.from_param(self._matrix, self.func)
            or Matrix.from_video(self.work_clip, self.strict, self.func)
        )

    @cachedproperty
    def color_range(self) -> ColorRange:
        return (
            ColorRange.from_param(self._range_in, self.func)
            or ColorRange.from_video(self.work_clip, self.strict, self.func)
        )

    @property
    def is_float(self) -> bool:
        """Whether the clip is of float sample type."""

        return self.norm_clip.format.sample_type is vs.FLOAT

    @property
    def is_integer(self) -> bool:
        """Whether the clip is of integer sample type."""

        return self.norm_clip.format.sample_type is vs.INTEGER

    @property
    def is_hd(self) -> bool:
        """Whether the clip has an HD resolution (>= 1280x720)."""

        return self.work_clip.width >= 1280 or self.work_clip.height >= 720

    @property
    def luma(self) -> bool:
        """Whether to process luma."""

        return 0 in self

    @property
    def luma_only(self) -> bool:
        """Whether luma is the only channel that is getting processed."""

        return self == [0]

    @property
    def chroma(self) -> bool:
        """Whether any of the two chroma planes are getting processed."""

        return 1 in self or 2 in self

    @property
    def chroma_only(self) -> bool:
        """Whether both of the two chroma planes are getting processed."""

        return self == [1, 2]

    @property
    def chroma_pplanes(self) -> list[int]:
        """Which chroma planes are getting processed."""

        return list({*self} - {0})

    def normalize_planes(self, planes: PlanesT) -> list[int]:
        return normalize_planes(self.work_clip, planes)

    def with_planes(self, planes: PlanesT) -> list[int]:
        return self.normalize_planes(sorted(set(self + self.normalize_planes(planes))))

    def without_planes(self, planes: PlanesT) -> list[int]:
        return self.normalize_planes(sorted(set(self) - {*self.normalize_planes(planes)}))

    def return_clip(self, processed: vs.VideoNode) -> vs.VideoNode:
        """
        Function used at the end of the function, to convert back to original format and
        optionally bitdepth, merge back chroma.
        """

        assert check_variable(processed, self.func)

        if len(self.chroma_planes):
            processed = join([processed, *self.chroma_planes], self.clip.format.color_family)

        if self.cfamily_converted:
            from ..utils import Colorspace

            processed = Colorspace.OPP.to_rgb(processed)

        if self.bitdepth:
            processed = depth(processed, self.clip)

        if self.chroma_only:
            processed = join(self.clip, processed)

        return processed

    def norm_seq(self, seq: T | Sequence[T], null: T = 0) -> list[T]:  # type: ignore
        """
        Normalize a value or sequence to a list mapped to the clip's planes.
        Unprocessed planes will get "null" value.
        """

        return [
            x if i in self else null
            for i, x in enumerate(normalize_seq(seq, self.num_planes))
        ]
