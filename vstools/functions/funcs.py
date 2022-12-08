from __future__ import annotations

from typing import Callable, Concatenate, Iterable, overload

import vapoursynth as vs

from ..exceptions import CustomRuntimeError, InvalidColorFamilyError
from ..types import (
    MISSING, ConstantFormatVideoNode, FuncExceptT, HoldsVideoFormatT, KwargsT, MissingT, P, PlanesT, R, T, VideoFormatT,
    cachedproperty
)
from .check import check_variable
from .normalize import normalize_planes, to_arr
from .utils import join, plane, split

__all__ = [
    'iterate', 'fallback', 'kwargs_fallback',

    'PlaneParser'
]


def iterate(
    base: T, function: Callable[Concatenate[T | R, P], T | R],
    count: int, *args: P.args, **kwargs: P.kwargs
) -> T | R:
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
    return fallback(value, kwargs[0].get(kwargs[1], None), *fallbacks, default=default)


class PlaneParser(cachedproperty.baseclass, list[int]):
    def __init__(
        self, clip: vs.VideoNode, func: FuncExceptT, planes: PlanesT = None,
        color_family: VideoFormatT | HoldsVideoFormatT | vs.ColorFamily | Iterable[
            VideoFormatT | HoldsVideoFormatT | vs.ColorFamily
        ] | None = None, strict: bool = True
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
        self.converted = False

        super().__init__(normalize_planes(self.norm_clip, planes))

    @cachedproperty
    def norm_clip(self) -> ConstantFormatVideoNode:
        fmt = self.clip.format
        clip: vs.VideoNode = self.clip

        cfamily = fmt.color_family

        if not self.allowed_cfamilies or cfamily in self.allowed_cfamilies:
            return clip  # type: ignore

        if cfamily is vs.RGB:
            if hasattr(vs.core, 'fmtc'):
                clip = clip.fmtc.matrix(
                    fulls=True, fulld=True, col_fam=vs.RGB, coef=[
                        1, 1, 2 / 3, 0, 1, 0, -4 / 3, 0, 1, -1, 2 / 3, 0
                    ]
                )
            else:
                from ..utils import get_neutral_value

                diff = '' if fmt.bits_per_sample == 32 else f'{get_neutral_value(clip)} +'

                R, G, B = split(clip)

                clip = join([
                    vs.core.std.Expr([R, G, B], 'x y z + + 1 3 / *'),
                    vs.core.std.Expr([R, B], f'x y - 1 2 / * {diff}'),
                    vs.core.std.Expr([R, G, B], f'x z + 1 4 / * y 1 2 / * - {diff}')
                ], vs.YUV)

            self.converted = True

        if cfamily is vs.YUV and vs.GRAY in self.allowed_cfamilies:
            clip = plane(clip, 0)

        return clip  # type: ignore

    @cachedproperty
    def work_clip(self) -> vs.VideoNode:
        return plane(self.norm_clip, 0) if self == [0] else self.clip

    @cachedproperty
    def chroma_planes(self) -> list[vs.VideoNode]:
        if self != [0] or self.norm_clip.format.num_planes == 1:
            return []
        return [plane(self.norm_clip, i) for i in {1, 2}]

    @property
    def is_float(self) -> bool:
        return self.norm_clip.format.sample_type is vs.FLOAT

    @property
    def is_integer(self) -> bool:
        return self.norm_clip.format.sample_type is vs.INTEGER

    @property
    def luma(self) -> bool:
        return 0 in self

    @property
    def luma_only(self) -> bool:
        return self == [0]

    @property
    def chroma(self) -> bool:
        return 1 in self or 2 in self

    @property
    def chroma_only(self) -> bool:
        return self == [1, 2]

    def return_clip(self, processed: vs.VideoNode) -> vs.VideoNode:
        assert check_variable(processed, self.func)

        fmt = processed.format

        if len(self.chroma_planes):
            processed = join([processed, *self.chroma_planes], self.clip.format.color_family)

        if self.converted:
            if hasattr(vs.core, 'fmtc'):
                processed = processed.fmtc.matrix(
                    fulls=True, fulld=True, col_fam=vs.YUV, coef=[
                        1 / 3, 1 / 3, 1 / 3, 0, 1 / 2, 0, -1 / 2, 0, 1 / 4, -1 / 2, 1 / 4, 0
                    ]
                )
            else:
                from ..utils import get_neutral_value

                diff = '' if fmt.bits_per_sample == 32 else f'{get_neutral_value(processed)} -'

                Y, U, V = split(processed)

                processed = join([
                    vs.core.std.Expr([Y, U, V], f'x y {diff} + z {diff} 2 3 / * +'),
                    vs.core.std.Expr([Y, V], f'x y {diff} 4 3 / * -'),
                    vs.core.std.Expr([Y, U, V], f'x z {diff} 2 3 / * + y {diff} -')
                ], vs.RGB)

        return processed
