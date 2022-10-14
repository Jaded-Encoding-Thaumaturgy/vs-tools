from __future__ import annotations

import inspect
from functools import partial, wraps
from typing import Any, Callable, cast, overload

import vapoursynth as vs

from ..enums import (
    ChromaLocation, ChromaLocationT, ColorRange, ColorRangeT, FieldBased, FieldBasedT, Matrix, MatrixT, Primaries,
    PrimariesT, Transfer, TransferT
)
from ..exceptions import CustomValueError
from ..functions import depth
from ..types import F_VD, FuncExceptT
from .info import get_depth

__all__ = [
    'finalize_clip',
    'finalize_output',
    'initialize_clip',
    'initialize_input'
]


# Original from vardefunc, thanks Vardë

def finalize_clip(
    clip: vs.VideoNode, bits: int | None = 10, clamp_tv_range: bool = True, *, func: FuncExceptT | None = None
) -> vs.VideoNode:
    if bits:
        clip = depth(clip, bits)
    else:
        bits = get_depth(clip)

    if clamp_tv_range:
        clip = clip.std.Expr([
            f'x {16 << (bits - 8)} max {235 << (bits - 8)} min',
            f'x {16 << (bits - 8)} max {240 << (bits - 8)} min'
        ])
    return clip


@overload
def finalize_output(
    *, bits: int | None = 10, clamp_tv_range: bool = True, func: FuncExceptT | None = None
) -> Callable[[F_VD], F_VD]:
    ...


@overload
def finalize_output(function: F_VD | None, /, *, func: FuncExceptT | None = None) -> F_VD:
    ...


def finalize_output(
    function: F_VD | None = None, /, *, bits: int | None = 10,
    clamp_tv_range: bool = True, func: FuncExceptT | None = None
) -> Callable[[F_VD], F_VD] | F_VD:
    if function is None:
        return cast(
            Callable[[F_VD], F_VD],
            partial(finalize_output, bits=bits, clamp_tv_range=clamp_tv_range)
        )

    @wraps(function)
    def _wrapper(*args: Any, **kwargs: Any) -> vs.VideoNode:
        assert function
        return finalize_clip(function(*args, **kwargs), bits, clamp_tv_range, func=func)

    return cast(F_VD, _wrapper)


def initialize_clip(
    clip: vs.VideoNode, bits: int = 16,
    matrix: MatrixT = Matrix.BT709,
    transfer: TransferT = Transfer.BT709,
    primaries: PrimariesT = Primaries.BT709,
    chroma_location: ChromaLocationT = ChromaLocation.LEFT,
    color_range: ColorRangeT = ColorRange.LIMITED,
    field_based: FieldBasedT = FieldBased.PROGRESSIVE,
    *, func: FuncExceptT | None = None
) -> vs.VideoNode:
    clip = clip.std.SetFrameProps(
        _Matrix=matrix, _Transfer=transfer, _Primaries=primaries,
        _ChromaLocation=chroma_location, _ColorRange=color_range
    )

    clip = FieldBased.ensure_presence(clip, field_based, func)

    return depth(clip, bits)


@overload
def initialize_input(
    *, bits: int = ...,
    matrix: MatrixT = Matrix.BT709,
    transfer: TransferT = Transfer.BT709,
    primaries: PrimariesT = Primaries.BT709,
    chroma_location: ChromaLocationT = ChromaLocation.LEFT,
    field_based: FieldBasedT = FieldBased.PROGRESSIVE,
    func: FuncExceptT | None = None
) -> Callable[[F_VD], F_VD]:
    ...


@overload
def initialize_input(function: F_VD | None, /, *, func: FuncExceptT | None = None) -> F_VD:
    ...


def initialize_input(
    function: F_VD | None = None, /, *, bits: int = 16,
    matrix: MatrixT = Matrix.BT709,
    transfer: TransferT = Transfer.BT709,
    primaries: PrimariesT = Primaries.BT709,
    chroma_location: ChromaLocationT = ChromaLocation.LEFT,
    color_range: ColorRangeT = ColorRange.LIMITED,
    field_based: FieldBasedT = FieldBased.PROGRESSIVE,
    func: FuncExceptT | None = None
) -> Callable[[F_VD], F_VD] | F_VD:
    """
    Decorator implementation of ``initialize_clip``
    """
    if function is None:
        return cast(
            Callable[[F_VD], F_VD],
            partial(
                initialize_input, bits=bits, matrix=matrix, transfer=transfer,
                primaries=primaries, field_based=field_based, func=func
            )
        )

    init_args = dict[str, Any](
        bits=bits,
        matrix=matrix, transfer=transfer, primaries=primaries,
        chroma_location=chroma_location, color_range=color_range,
        func=func
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
            'initialize_input: None VideoNode found in positional, keyword nor default arguments!'
        )

    return cast(F_VD, _wrapper)
