from __future__ import annotations

from typing import Callable, Concatenate, Iterable, Sequence, overload

import vapoursynth as vs

from ..exceptions import CustomRuntimeError, InvalidColorFamilyError
from ..types import (
    MISSING, ConstantFormatVideoNode, FuncExceptT, HoldsVideoFormatT, KwargsT, MissingT, P, PlanesT, R, T, VideoFormatT,
    cachedproperty
)
from .check import check_variable
from .normalize import normalize_planes, normalize_seq, to_arr
from .utils import depth, join, plane

__all__ = [
    'iterate', 'fallback', 'kwargs_fallback',

    'FunctionUtil'
]


def iterate(
    base: T, function: Callable[Concatenate[T | R, P], T | R],
    count: int, *args: P.args, **kwargs: P.kwargs
) -> T | R:
    """
    Execute a given function over the clip multiple times.

    Different from regular iteration functions is that you do not need to pass a partial object.
    This function accepts *args and **kwargs. These will be passed on to the given function.

    Examples:

    >>> iterate(5, lambda x: x * 2, 2)
        20

    >>> iterate(clip, core.std.Maximum, 3, threshold=0.5)
        VideoNode

    :param base:        Base clip, value, etc. to iterate over.
    :param function:    Function to iterate over the base.
    :param count:       Number of times to execute function.
    :param *args:       Positional arguments to pass to the given function.
    :param **kwargs:    Keyword arguments to pass to the given function.

    :return:            Clip, value, etc. with the given function run over it
                        *n* amount of times based on the given count.
    """

    if count <= 0:
        return base

    result: T | R = base

    for _ in range(count):
        result = function(result, *args, **kwargs)

    return result


fallback_missing = object()


@overload
def fallback(value: T | None, fallback: T) -> T:
    ...


@overload
def fallback(value: T | None, fallback0: T | None, default: T) -> T:
    ...


@overload
def fallback(value: T | None, fallback0: T | None, fallback1: T | None, default: T) -> T:
    ...


@overload
def fallback(value: T | None, *fallbacks: T | None) -> T | MissingT:
    ...


@overload
def fallback(value: T | None, *fallbacks: T | None, default: T) -> T:
    ...


def fallback(value: T | None, *fallbacks: T | None, default: T = fallback_missing) -> T | MissingT:  # type: ignore
    """
    Utility function that returns a value or a fallback if the value is None.

    Example:

    .. code-block:: python

        >>> fallback(5, 6)
        5
        >>> fallback(None, 6)
        6

    :param value:               Input value to evaluate. Can be None.
    :param fallback_value:      Value to return if the input value is None.

    :return:                    Input value or fallback value if input value is None.
    """

    if value is not None:
        return value

    for fallback in fallbacks:
        if fallback is not None:
            return fallback

    if default is not fallback_missing:
        return default
    elif len(fallbacks) > 3:
        return MISSING

    raise CustomRuntimeError('You need to specify a default/fallback value!')


@overload
def kwargs_fallback(
    input_value: T | None, kwargs: tuple[KwargsT, str], fallback: T
) -> T:
    ...


@overload
def kwargs_fallback(
    input_value: T | None, kwargs: tuple[KwargsT, str], fallback0: T | None, default: T
) -> T:
    ...


@overload
def kwargs_fallback(
    input_value: T | None, kwargs: tuple[KwargsT, str], fallback0: T | None, fallback1: T | None,
    default: T
) -> T:
    ...


@overload
def kwargs_fallback(
    input_value: T | None, kwargs: tuple[KwargsT, str], *fallbacks: T | None
) -> T | MissingT:
    ...


@overload
def kwargs_fallback(
    input_value: T | None, kwargs: tuple[KwargsT, str], *fallbacks: T | None, default: T
) -> T:
    ...


def kwargs_fallback(  # type: ignore
    value: T | None, kwargs: tuple[KwargsT, str], *fallbacks: T | None, default: T = fallback_missing  # type: ignore
) -> T | MissingT:
    """Utility function to return a fallback value from kwargs if value was not found or is None."""

    return fallback(value, kwargs[0].get(kwargs[1], None), *fallbacks, default=default)


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
        ] | None = None, bitdepth: int | range | None = None, strict: bool = False
    ) -> None:
        from ..utils import get_color_family

        assert check_variable(clip, func)

        if color_family is not None:
            color_family = [get_color_family(c) for c in to_arr(color_family)]  # type: ignore

            if strict:
                InvalidColorFamilyError.check(clip, color_family, func)

        self.clip = clip
        self.planes = planes
        self.func = func
        self.strict = strict
        self.allowed_cfamilies = color_family
        self.cfamily_converted = False
        self.bitdepth = bitdepth

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
