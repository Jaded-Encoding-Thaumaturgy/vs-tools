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
        - Automatically dither up and down as required.
        - Automatically check if the input clip has variable formats, resolutions, etc.
        - Fully type safe and removes the need for asserts or typeguards in function code.
        - Handy properties for common code paths, improving code readability and writability.

    Examples:

    .. code-block:: python

        >>> func = FunctionUtil(clip, planes=0, color_family=(vs.YUV, vs.GRAY), bitdepth=16)
        >>> wclip = func.work_clip
        >>> txt = wclip.text.Text("This clip has been processed!")
        >>> return func.return_clip(txt)

    For further examples, see: <https://github.com/search?q=org%3AJaded-Encoding-Thaumaturgy+FunctionUtil>
    """

    def __init__(
        self, clip: vs.VideoNode, func: FuncExceptT, planes: PlanesT = None,
        color_family: VideoFormatT | HoldsVideoFormatT | vs.ColorFamily | Iterable[
            VideoFormatT | HoldsVideoFormatT | vs.ColorFamily
        ] | None = None, bitdepth: int | range | tuple[int, int] | set[int] | None = None, strict: bool = False,
        *, matrix: MatrixT | None = None, range_in: ColorRangeT | None = None
    ) -> None:
        """
        :param clip:            Clip to process.
        :param func:            Function returned for custom error handling.
                                This should only be set by VS package developers.
        :param planes:          Planes that get processed in the function. Default: All planes.
        :param color_family:    Accepted color families. If the input does not adhere to these,
                                it will be converted automatically. Additionaly, if `planes=0`,
                                it will extract the luma for processing, and merge back the chroma planes
                                in `return_clip`. If the input clip is RGB and `planes=0`, it will be
                                converted to YUV and back again to retrieve the luma plane.
                                Default: All families.
        :param bitdepth:        The bitdepth or range of bitdepths to work with. Can be an int, range, tuple, or set.
                                If a range or set is provided and `strict=False`,
                                automatically convert the work clip to the highest bitdepth allowed.
                                Range or tuple indicates a range of allowed bitdepths,
                                set indicates specific allowed bitdepths.
                                If an int is provided, set the clip's bitdepth to that value.
                                `return_clip` automatically restores the clip to the original bitdepth.
                                If None, use the input clip's bitdepth. Default: None.
        :param strict:          Be strict about the input clip's properties.
                                If True, the input clip must adhere to the given number of planes,
                                the color family, and the bitdepth. If False, all these properties
                                will be applied as necessary. Default: False.
        :param matrix:          Color Matrix to work in. Used for YUV <-> RGB conversions.
                                Default: Get matrix from the input clip.
        :param range_in:        Color Range to work in. Used for bitdepth conversions.
                                Default: Get the color range from the input clip.
        """
        from ..utils import get_color_family

        assert check_variable(clip, func)

        if color_family is not None:
            color_family = [get_color_family(c) for c in to_arr(color_family)]

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
        """Get a "normalized" clip. This means color space and bitdepth are converted if necessary."""

        from .. import get_depth

        if isinstance(self.bitdepth, (range, set)) and self.clip.format.bits_per_sample not in self.bitdepth:
            clip = depth(self.clip, min(bits for bits in self.bitdepth if bits >= get_depth(self.clip)))
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
        """Get a list of all chroma planes in the normalised clip."""

        if self == [0] or self.norm_clip.format.num_planes == 1:
            return []

        return [plane(self.norm_clip, i) for i in (1, 2)]

    @cachedproperty
    def matrix(self) -> Matrix:
        """Get the clip's matrix."""

        return Matrix.from_param_or_video(self._matrix, self.work_clip, self.strict, self.func)

    @cachedproperty
    def color_range(self) -> ColorRange:
        """Get the clip's color range."""

        return ColorRange.from_param_or_video(self._range_in, self.work_clip, self.strict, self.func)

    @property
    def is_float(self) -> bool:
        """Whether the clip is of a float sample type."""

        return self.norm_clip.format.sample_type is vs.FLOAT

    @property
    def is_integer(self) -> bool:
        """Whether the clip is of an integer sample type."""

        return self.norm_clip.format.sample_type is vs.INTEGER

    @property
    def is_hd(self) -> bool:
        """Whether the clip is of an HD resolution (>= 1280x720)."""

        return self.work_clip.width >= 1280 or self.work_clip.height >= 720

    @property
    def luma(self) -> bool:
        """Whether the luma gets processed."""

        return 0 in self

    @property
    def luma_only(self) -> bool:
        """Whether luma is the only channel that gets processed."""

        return self == [0]

    @property
    def chroma(self) -> bool:
        """Whether any chroma planes get processed."""

        return 1 in self or 2 in self

    @property
    def chroma_only(self) -> bool:
        """Whether only chroma planes get processed."""

        return self == [1, 2]

    @property
    def chroma_pplanes(self) -> list[int]:
        """
        A list of which chroma planes get processed based on the work clip.

        This means that if you pass [0, 1, 2] but passed a GRAY clip, it will only return [0].
        Similarly, if you pass GRAY and it gets converted to RGB, this will return [0, 1, 2].
        """

        return list({*self} - {0})

    def normalize_planes(self, planes: PlanesT) -> list[int]:
        """Normalize the given sequence of planes."""

        return normalize_planes(self.work_clip, planes)

    def with_planes(self, planes: PlanesT) -> list[int]:
        return self.normalize_planes(sorted(set(self + self.normalize_planes(planes))))

    def without_planes(self, planes: PlanesT) -> list[int]:
        return self.normalize_planes(sorted(set(self) - {*self.normalize_planes(planes)}))

    def return_clip(self, processed: vs.VideoNode) -> vs.VideoNode:
        """
        Merge back the chroma if necessary and convert the processed clip back to the original clip's format.
        If `bitdepth != None`, the bitdepth will also be converted if necessary.

        :param processed:       The clip with all the processing applied to it.

        :return:                Processed clip converted back to the original input clip's format.
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
        Unprocessed planes will be set to the given "null" value.
        """

        return [
            x if i in self else null
            for i, x in enumerate(normalize_seq(seq, self.num_planes))
        ]
