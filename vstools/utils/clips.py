from __future__ import annotations

import inspect
from functools import partial, wraps
from typing import Any, Callable, Concatenate, cast, overload

from ..enums import (
    ChromaLocation, ChromaLocationT, ColorRange, ColorRangeT, FieldBased, FieldBasedT, Matrix, MatrixT, Primaries,
    PrimariesT, PropEnum, Transfer, TransferT
)
from ..exceptions import CustomValueError, InvalidColorFamilyError
from ..functions import check_variable, depth, fallback, get_y, join
from ..types import F_VD, FuncExceptT, HoldsVideoFormatT, P
from . import vs_proxy as vs
from .info import get_depth, get_video_format, get_w
from .scale import scale_8bit

__all__ = [
    'finalize_clip',
    'finalize_output',
    'initialize_clip',
    'initialize_input',
    'chroma_injector',
    'allow_variable_clip'
]


def finalize_clip(
    clip: vs.VideoNode, bits: int | None = 10, clamp_tv_range: bool = True, *, func: FuncExceptT | None = None
) -> vs.VideoNode:
    assert check_variable(clip, func or finalize_clip)

    if bits:
        clip = depth(clip, bits)
    else:
        bits = get_depth(clip)

    if clamp_tv_range:
        low_luma, high_luma = scale_8bit(clip, 16), scale_8bit(clip, 235)
        low_chroma, high_chroma = scale_8bit(clip, 16, True), scale_8bit(clip, 240, True)

        if hasattr(vs.core, 'akarin'):
            clip = clip.akarin.Expr([
                f'x {low_luma} {high_luma} clamp', f'x {low_chroma} {high_chroma} clamp'
            ])
        else:
            clip = clip.std.Expr([
                f'x {low_luma} max {high_luma} min', f'x {low_chroma} max {high_chroma} min'
            ])

    return clip


@overload
def finalize_output(
    function: None = None, /, *, bits: int | None = 10,
    clamp_tv_range: bool = True, func: FuncExceptT | None = None
) -> Callable[[F_VD], F_VD] | F_VD:
    ...


@overload
def finalize_output(
    function: F_VD, /, *, bits: int | None = 10,
    clamp_tv_range: bool = True, func: FuncExceptT | None = None
) -> F_VD:
    ...


def finalize_output(
    function: F_VD | None = None, /, *, bits: int | None = 10,
    clamp_tv_range: bool = True, func: FuncExceptT | None = None
) -> Callable[[F_VD], F_VD] | F_VD:
    if function is None:
        return cast(
            Callable[[F_VD], F_VD],
            partial(finalize_output, bits=bits, clamp_tv_range=clamp_tv_range, func=func)
        )

    @wraps(function)
    def _wrapper(*args: Any, **kwargs: Any) -> vs.VideoNode:
        assert function
        return finalize_clip(function(*args, **kwargs), bits, clamp_tv_range, func=func)

    return cast(F_VD, _wrapper)


def initialize_clip(
    clip: vs.VideoNode, bits: int | None = 16,
    matrix: MatrixT | None = Matrix.BT709,
    transfer: TransferT | None = Transfer.BT709,
    primaries: PrimariesT | None = Primaries.BT709,
    chroma_location: ChromaLocationT | None = ChromaLocation.LEFT,
    color_range: ColorRangeT | None = ColorRange.LIMITED,
    field_based: FieldBasedT | None = FieldBased.PROGRESSIVE,
    strict: bool = False, *, func: FuncExceptT | None = None
) -> vs.VideoNode:
    func = fallback(func, initialize_clip)  # type: ignore

    values: list[tuple[type[PropEnum], Any]] = [
        (Matrix, matrix),
        (Transfer, transfer),
        (Primaries, primaries),
        (ChromaLocation, chroma_location),
        (ColorRange, color_range),
        (FieldBased, field_based)
    ]

    clip = PropEnum.ensure_presences(clip, [
        (cls if strict else cls.from_video(clip, False, func)) if value is None else cls.from_param(value, func)
        for cls, value in values
    ], func)

    if bits is None:
        return clip

    return depth(clip, bits)


@overload
def initialize_input(
    function: None = None, /, *, bits: int | None = 16,
    matrix: MatrixT | None = Matrix.BT709,
    transfer: TransferT | None = Transfer.BT709,
    primaries: PrimariesT | None = Primaries.BT709,
    chroma_location: ChromaLocationT | None = ChromaLocation.LEFT,
    color_range: ColorRangeT | None = ColorRange.LIMITED,
    field_based: FieldBasedT | None = FieldBased.PROGRESSIVE,
    func: FuncExceptT | None = None
) -> Callable[[F_VD], F_VD]:
    ...


@overload
def initialize_input(
    function: F_VD, /, *, bits: int | None = 16,
    matrix: MatrixT | None = Matrix.BT709,
    transfer: TransferT | None = Transfer.BT709,
    primaries: PrimariesT | None = Primaries.BT709,
    chroma_location: ChromaLocationT | None = ChromaLocation.LEFT,
    color_range: ColorRangeT | None = ColorRange.LIMITED,
    field_based: FieldBasedT | None = FieldBased.PROGRESSIVE,
    strict: bool = False, func: FuncExceptT | None = None
) -> F_VD:
    ...


def initialize_input(
    function: F_VD | None = None, /, *, bits: int | None = 16,
    matrix: MatrixT | None = Matrix.BT709,
    transfer: TransferT | None = Transfer.BT709,
    primaries: PrimariesT | None = Primaries.BT709,
    chroma_location: ChromaLocationT | None = ChromaLocation.LEFT,
    color_range: ColorRangeT | None = ColorRange.LIMITED,
    field_based: FieldBasedT | None = FieldBased.PROGRESSIVE,
    strict: bool = False, func: FuncExceptT | None = None
) -> Callable[[F_VD], F_VD] | F_VD:
    """
    Decorator implementation of ``initialize_clip``
    """
    if function is None:
        return cast(
            Callable[[F_VD], F_VD],
            partial(
                initialize_input, bits=bits, matrix=matrix, transfer=transfer,
                primaries=primaries, field_based=field_based, strict=strict, func=func
            )
        )

    init_args = dict[str, Any](
        bits=bits,
        matrix=matrix, transfer=transfer, primaries=primaries,
        chroma_location=chroma_location, color_range=color_range,
        strict=strict, func=func
    )

    @wraps(function)
    def _wrapper(*args: Any, **kwargs: Any) -> vs.VideoNode:
        assert function

        args_l = list(args)
        for i, obj in enumerate(args_l):
            if isinstance(obj, vs.VideoNode):
                args_l[i] = initialize_clip(obj, **init_args)
                return function(*args_l, **kwargs)

        kwargs2 = kwargs.copy()
        for name, obj in kwargs2.items():
            if isinstance(obj, vs.VideoNode):
                kwargs2[name] = initialize_clip(obj, **init_args)
                return function(*args, **kwargs2)

        for name, param in inspect.signature(function).parameters.items():
            if param.default is not inspect.Parameter.empty and isinstance(param.default, vs.VideoNode):
                return function(*args, **kwargs2 | {name: initialize_clip(param.default, **init_args)})

        raise CustomValueError(
            'No VideoNode found in positional, keyword nor default arguments!', func or initialize_input
        )

    return cast(F_VD, _wrapper)


@overload
def chroma_injector(
    function: None = None, *,
    scaler: Callable[[vs.VideoNode, int, int, int], vs.VideoNode] = vs.core.lazy.resize.Bicubic,
    func: FuncExceptT | None = None
) -> Callable[[F_VD], F_VD]:
    ...


@overload
def chroma_injector(
    function: F_VD, *,
    scaler: Callable[[vs.VideoNode, int, int, int], vs.VideoNode] = vs.core.lazy.resize.Bicubic,
    func: FuncExceptT | None = None
) -> F_VD:
    ...


def chroma_injector(
    function: F_VD | None = None, *,
    scaler: Callable[[vs.VideoNode, int, int, int], vs.VideoNode] = vs.core.lazy.resize.Bicubic,
    func: FuncExceptT | None = None
) -> Callable[[F_VD], F_VD] | F_VD:
    if function is None:
        return cast(
            Callable[[F_VD], F_VD],
            partial(chroma_injector, scaler=scaler, func=func)
        )

    @wraps(function)
    def inner(_chroma: vs.VideoNode, clip: vs.VideoNode, *args: Any, **kwargs: Any) -> vs.VideoNode:
        assert function

        _cached_clips = dict[str, vs.VideoNode]()

        def upscale_chroma(n: int, f: vs.VideoFrame) -> vs.VideoNode:
            key = f'{f.width}_{f.height}_{f.format.id}'

            if key not in _cached_clips:
                fmt = vs.core.query_video_format(
                    vs.YUV, f.format.sample_type, f.format.bits_per_sample
                ) if out_fmt is None else out_fmt

                _cached_clips[key] = join(
                    y.resize.Point(f.width, f.height, f.format.id),
                    scaler(_chroma, f.width, f.height, fmt.id),
                    vs.YUV
                )

            return _cached_clips[key]

        fmt = get_video_format(clip)
        out_fmt: vs.VideoFormat | None = None

        if clip.format is not None:
            InvalidColorFamilyError.check(clip, (vs.GRAY, vs.YUV), func or chroma_injector)

            in_fmt = vs.core.query_video_format(vs.GRAY, fmt.sample_type, fmt.bits_per_sample)
            out_fmt = vs.core.query_video_format(vs.YUV, fmt.sample_type, fmt.bits_per_sample)

            y = allow_variable_clip(get_y, format=in_fmt)(clip)
        else:
            y = allow_variable_clip(get_y)(clip)

        if y.width != 0 and y.height != 0 and out_fmt is not None:
            clip_in = join(y, scaler(_chroma, y.width, y.height, out_fmt.id), vs.YUV)
        else:
            clip_in = (
                y.resize.Point(format=out_fmt.id) if out_fmt is not None else y
            ).std.FrameEval(upscale_chroma, y)

        result = function(clip_in, *args, **kwargs)

        if result.format is None:
            return allow_variable_clip(get_y)(result)

        InvalidColorFamilyError.check(
            result, (vs.GRAY, vs.YUV), chroma_injector,
            'Can only decorate function returning clips having {correct} color family!'
        )

        if result.format.color_family == vs.GRAY:
            return result

        res_fmt = vs.core.query_video_format(
            vs.GRAY, result.format.sample_type, result.format.bits_per_sample
        )

        return allow_variable_clip(get_y, format=res_fmt)(result)

    return cast(F_VD, inner)


@overload
def allow_variable_clip(
    function: None = None,
    width: int | None = None, height: int | None = None, format: int | HoldsVideoFormatT | None = None,
    func: FuncExceptT | None = None
) -> Callable[
    [Callable[Concatenate[vs.VideoNode, P], vs.VideoNode]],
    Callable[Concatenate[vs.VideoNode, P], vs.VideoNode]
]:
    ...


@overload
def allow_variable_clip(
    function: Callable[Concatenate[vs.VideoNode, P], vs.VideoNode],
    width: int | None = None, height: int | None = None, format: int | HoldsVideoFormatT | None = None,
    func: FuncExceptT | None = None
) -> Callable[Concatenate[vs.VideoNode, P], vs.VideoNode]:
    ...


def allow_variable_clip(
    function: Callable[Concatenate[vs.VideoNode, P], vs.VideoNode] | None = None,
    width: int | None = None, height: int | None = None, format: int | HoldsVideoFormatT | None = None,
    func: FuncExceptT | None = None
) -> Callable[
    [Callable[Concatenate[vs.VideoNode, P], vs.VideoNode]],
    Callable[Concatenate[vs.VideoNode, P], vs.VideoNode]
] | Callable[Concatenate[vs.VideoNode, P], vs.VideoNode]:
    if function is None:
        return cast(
            Callable[
                [Callable[Concatenate[vs.VideoNode, P], vs.VideoNode]],
                Callable[Concatenate[vs.VideoNode, P], vs.VideoNode]
            ], partial(chroma_injector, width=width, height=height, format=format, func=func)
        )

    wrapped_function = function

    out_fmt = None if format is None else get_video_format(format).id

    if height is not None and width:
        width = get_w(height, )

    @wraps(function)
    def inner2(clip: vs.VideoNode, *args: P.args, **kwargs: P.kwargs) -> vs.VideoNode:
        if out_fmt:
            clip_out = clip.resize.Point(format=out_fmt)

            def frameeval_wrapper(n: int, f: vs.VideoFrame) -> vs.VideoNode:
                return wrapped_function(
                    clip.resize.Point(f.width, f.height, f.format.id), *args, **kwargs
                ).resize.Point(format=out_fmt)
        else:
            clip_out = clip

            def frameeval_wrapper(n: int, f: vs.VideoFrame) -> vs.VideoNode:
                return wrapped_function(
                    clip.resize.Point(f.width, f.height, f.format.id), *args, **kwargs
                )

        if width is not None or height is not None:
            clip_out = clip_out.resize.Point(
                width or clip_out.width, height or clip_out.height
            )

        return vs.core.std.FrameEval(clip_out, frameeval_wrapper, clip)

    return cast(Callable[Concatenate[vs.VideoNode, P], vs.VideoNode], inner2)
