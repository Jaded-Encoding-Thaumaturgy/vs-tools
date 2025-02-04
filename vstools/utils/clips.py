from __future__ import annotations

import inspect
from functools import partial, wraps
from typing import Any, Callable, Literal, TypeVar, cast, overload

from stgpytools import CustomValueError, FuncExceptT, KwargsT, T, fallback

from ..enums import (
    ChromaLocation, ChromaLocationT, ColorRange, ColorRangeT, FieldBased, FieldBasedT, Matrix, MatrixT, Primaries,
    PrimariesT, PropEnum, Transfer, TransferT
)
from ..functions import DitherType, check_variable, depth
from ..types import F_VD, HoldsVideoFormatT, VideoFormatT
from . import vs_proxy as vs
from .cache import DynamicClipsCache
from .info import get_depth

__all__ = [
    'finalize_clip',
    'finalize_output',
    'initialize_clip',
    'initialize_input',

    'ProcessVariableClip',
    'ProcessVariableResClip',
    'ProcessVariableFormatClip',
    'ProcessVariableResFormatClip'
]


def finalize_clip(
    clip: vs.VideoNode,
    bits: VideoFormatT | HoldsVideoFormatT | int | None = 10,
    clamp_tv_range: bool | None = None,
    dither_type: DitherType = DitherType.AUTO,
    *, func: FuncExceptT | None = None
) -> vs.VideoNode:
    """
    Finalize a clip for output to the encoder.

    :param clip:            Clip to output.
    :param bits:            Bitdepth to output to.
    :param clamp_tv_range:  Whether to clamp to tv range. If None, decide based on clip properties.
    :param dither_type:     Dithering used for the bitdepth conversion.
    :param func:            Function returned for custom error handling.
                            This should only be set by VS package developers.

    :return:                Dithered down and optionally clamped clip.
    """
    from ..functions import limiter

    assert check_variable(clip, func or finalize_clip)

    if bits:
        clip = depth(clip, bits, dither_type=dither_type)

    if clamp_tv_range is None:
        try:
            clamp_tv_range = ColorRange.from_video(clip, strict=True).is_limited
        except Exception:
            clamp_tv_range = True

    if clamp_tv_range:
        clip = limiter(clip, tv_range=clamp_tv_range)

    return clip


@overload
def finalize_output(
    function: None = None, /, *, bits: int | None = 10,
    clamp_tv_range: bool = True, dither_type: DitherType = DitherType.AUTO, func: FuncExceptT | None = None
) -> Callable[[F_VD], F_VD] | F_VD:
    ...


@overload
def finalize_output(
    function: F_VD, /, *, bits: int | None = 10,
    clamp_tv_range: bool = True, dither_type: DitherType = DitherType.AUTO, func: FuncExceptT | None = None
) -> F_VD:
    ...


def finalize_output(
    function: F_VD | None = None, /, *, bits: int | None = 10,
    clamp_tv_range: bool = True, dither_type: DitherType = DitherType.AUTO, func: FuncExceptT | None = None
) -> Callable[[F_VD], F_VD] | F_VD:
    """Decorator implementation of finalize_clip."""

    if function is None:
        return cast(
            Callable[[F_VD], F_VD],
            partial(finalize_output, bits=bits, clamp_tv_range=clamp_tv_range, dither_type=dither_type, func=func)
        )

    @wraps(function)
    def _wrapper(*args: Any, **kwargs: Any) -> vs.VideoNode:
        assert function
        return finalize_clip(function(*args, **kwargs), bits, clamp_tv_range, dither_type, func=func)

    return cast(F_VD, _wrapper)


def initialize_clip(
    clip: vs.VideoNode, bits: int | None = None,
    matrix: MatrixT | None = None,
    transfer: TransferT | None = None,
    primaries: PrimariesT | None = None,
    chroma_location: ChromaLocationT | None = None,
    color_range: ColorRangeT | None = None,
    field_based: FieldBasedT | None = None,
    strict: bool = False,
    dither_type: DitherType = DitherType.AUTO, *, func: FuncExceptT | None = None
) -> vs.VideoNode:
    """
    Initialize a clip with default props.

    It is HIGHLY recommended to always use this function at the beginning of your scripts!

    :param clip:            Clip to initialize.
    :param bits:            Bits to dither to.
                            - If 0, no dithering is applied.
                            - If None, 16 if bit depth is lower than it, else leave untouched.
                            - If positive integer, dither to that bitdepth.
    :param matrix:          Matrix property to set. If None, tries to get the Matrix from existing props.
                            If no props are set or Matrix=2, guess from the video resolution.
    :param transfer:        Transfer property to set. If None, tries to get the Transfer from existing props.
                            If no props are set or Transfer=2, guess from the video resolution.
    :param primaries:       Primaries property to set. If None, tries to get the Primaries from existing props.
                            If no props are set or Primaries=2, guess from the video resolution.
    :param chroma_location: ChromaLocation prop to set. If None, tries to get the ChromaLocation from existing props.
                            If no props are set, guess from the video resolution.
    :param color_range:     ColorRange prop to set. If None, tries to get the ColorRange from existing props.
                            If no props are set, assume Limited Range.
    :param field_based:     FieldBased prop to set. If None, tries to get the FieldBased from existing props.
                            If no props are set, assume PROGRESSIVE.
    :param strict:          Whether to be strict about existing properties.
                            If True, throws an exception if certain frame properties are not found.
    :param dither_type:     Dithering used for the bitdepth conversion.
    :param func:            Function returned for custom error handling.
                            This should only be set by VS package developers.

    :return:                Clip with relevant frame properties set, and optionally dithered up to 16 bits by default.
    """

    func = fallback(func, initialize_clip)

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
        bits = max(get_depth(clip), 16)
    elif bits <= 0:
        return clip

    return depth(clip, bits, dither_type=dither_type)


@overload
def initialize_input(
    function: None = None, /, *, bits: int | None = 16,
    matrix: MatrixT | None = None,
    transfer: TransferT | None = None,
    primaries: PrimariesT | None = None,
    chroma_location: ChromaLocationT | None = None,
    color_range: ColorRangeT | None = None,
    field_based: FieldBasedT | None = None,
    dither_type: DitherType = DitherType.AUTO,
    func: FuncExceptT | None = None
) -> Callable[[F_VD], F_VD]:
    ...


@overload
def initialize_input(
    function: F_VD, /, *, bits: int | None = 16,
    matrix: MatrixT | None = None,
    transfer: TransferT | None = None,
    primaries: PrimariesT | None = None,
    chroma_location: ChromaLocationT | None = None,
    color_range: ColorRangeT | None = None,
    field_based: FieldBasedT | None = None,
    strict: bool = False,
    dither_type: DitherType = DitherType.AUTO, func: FuncExceptT | None = None
) -> F_VD:
    ...


def initialize_input(
    function: F_VD | None = None, /, *, bits: int | None = 16,
    matrix: MatrixT | None = None,
    transfer: TransferT | None = None,
    primaries: PrimariesT | None = None,
    chroma_location: ChromaLocationT | None = None,
    color_range: ColorRangeT | None = None,
    field_based: FieldBasedT | None = None,
    strict: bool = False,
    dither_type: DitherType = DitherType.AUTO, func: FuncExceptT | None = None
) -> Callable[[F_VD], F_VD] | F_VD:
    """
    Decorator implementation of ``initialize_clip``
    """

    init_args = dict[str, Any](
        bits=bits,
        matrix=matrix, transfer=transfer, primaries=primaries,
        chroma_location=chroma_location, color_range=color_range,
        field_based=field_based, strict=strict, dither_type=dither_type, func=func
    )

    if function is None:
        return cast(Callable[[F_VD], F_VD], partial(initialize_input, **init_args))

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
            'No VideoNode found in positional, keyword, nor default arguments!', func or initialize_input
        )

    return cast(F_VD, _wrapper)


class ProcessVariableClip(DynamicClipsCache[T]):
    def __init__(
        self, clip: vs.VideoNode,
        out_dim: tuple[int, int] | Literal[False] | None = None,
        out_fmt: int | vs.VideoFormat | Literal[False] | None = None,
        cache_size: int = 10
    ) -> None:
        bk_args = KwargsT(length=clip.num_frames, keep=True)

        if out_dim is None:
            out_dim = (clip.width, clip.height)

        if out_fmt is None:
            out_fmt = clip.format or False

        if out_dim is not False and 0 in out_dim:
            out_dim = False

        if out_dim is False:
            bk_args.update(width=8, height=8, varsize=True)
        else:
            bk_args.update(width=out_dim[0], height=out_dim[1])

        if out_fmt is False:
            bk_args.update(format=vs.GRAY8, varformat=True)
        else:
            bk_args.update(format=out_fmt)

        super().__init__(cache_size)

        self.clip, self.out = clip, clip.std.BlankClip(**bk_args)

    def eval_clip(self) -> vs.VideoNode:
        if self.out.format and (0 not in (self.out.width, self.out.height)):
            try:
                return self.get_clip(self.get_key(self.clip))
            except Exception:
                ...

        return self.out.std.FrameEval(lambda n, f: self[self.get_key(f)], self.clip)

    def get_clip(self, key: T) -> vs.VideoNode:
        return self.process(self.normalize(self.clip, key))

    @classmethod
    def from_clip(
        cls: type[ProcVarClipSelf],
        clip: vs.VideoNode
    ) -> vs.VideoNode:
        return cls(clip).eval_clip()

    @classmethod
    def from_func(
        cls: type[ProcVarClipSelf],
        clip: vs.VideoNode,
        func: Callable[[vs.VideoNode], vs.VideoNode],
        out_dim: tuple[int, int] | Literal[False] | None = None,
        out_fmt: int | vs.VideoFormat | Literal[False] | None = None,
        cache_size: int = 10
    ) -> vs.VideoNode:
        class _inner(cls):  # type: ignore
            process = staticmethod(func)

        return _inner(clip, out_dim, out_fmt, cache_size).eval_clip()

    def get_key(self, frame: vs.VideoFrame) -> T:
        raise NotImplementedError

    def normalize(self, clip: vs.VideoNode, cast_to: T) -> vs.VideoNode:
        raise NotImplementedError

    def process(self, clip: vs.VideoNode) -> vs.VideoNode:
        return clip


ProcVarClipSelf = TypeVar('ProcVarClipSelf', bound=ProcessVariableClip)  # type: ignore


class ProcessVariableResClip(ProcessVariableClip[tuple[int, int]]):
    def get_key(self, frame: vs.VideoFrame) -> tuple[int, int]:
        return (frame.width, frame.height)

    def normalize(self, clip: vs.VideoNode, cast_to: tuple[int, int]) -> vs.VideoNode:
        return clip.std.RemoveFrameProps().resize.Point(*cast_to).std.CopyFrameProps(clip)


class ProcessVariableFormatClip(ProcessVariableClip[vs.VideoFormat]):
    def get_key(self, frame: vs.VideoFrame) -> vs.VideoFormat:
        return frame.format

    def normalize(self, clip: vs.VideoNode, cast_to: vs.VideoFormat) -> vs.VideoNode:
        return clip.std.RemoveFrameProps().resize.Point(format=cast_to).std.CopyFrameProps(clip)


class ProcessVariableResFormatClip(ProcessVariableClip[tuple[int, int, vs.VideoFormat]]):
    def get_key(self, frame: vs.VideoFrame) -> tuple[int, int, vs.VideoFormat]:
        return (frame.width, frame.height, frame.format)

    def normalize(self, clip: vs.VideoNode, cast_to: tuple[int, int, vs.VideoFormat]) -> vs.VideoNode:
        return clip.std.RemoveFrameProps().resize.Point(*cast_to).std.CopyFrameProps(clip)
