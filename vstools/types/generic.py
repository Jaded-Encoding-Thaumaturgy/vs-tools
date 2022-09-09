from __future__ import annotations

from typing import Any, ByteString, Callable, Deque, Mapping, Protocol, Sequence, Set, TypeVar, Union

import vapoursynth as vs

from .builtins import (
    ByteData, ComparatorFunc, F, SingleOrArr, SingleOrArrOpt, SupportsAllComparisons, SupportsDunderGE,
    SupportsDunderGT, SupportsDunderLE, SupportsDunderLT, SupportsFloatOrIndex, SupportsRichComparison, SupportsString,
    SupportsTrunc
)

__all__ = [
    'MissingT', 'MISSING',

    'FuncExceptT', 'EnumFuncExceptT',

    'VideoPropT',

    'VideoFormatT',

    'HoldsVideoFormatT', 'HoldsPropValueT',

    'VSFunction',

    'StrArr', 'StrArrOpt',

    'PassthroughC',

    'AnythingElse',

    'ConstantFormatVideoNode'
]


class MissingT:
    ...


MISSING = MissingT()


VideoPropT = Union[
    int, Sequence[int],
    float, Sequence[float],
    str, Sequence[str],
    vs.VideoNode, Sequence[vs.VideoNode],
    vs.VideoFrame, Sequence[vs.VideoFrame],
    Callable[..., Any], Sequence[Callable[..., Any]]
]

VideoFormatT = Union[int, vs.PresetFormat, vs.VideoFormat]

HoldsVideoFormatT = Union[vs.VideoNode, vs.VideoFrame, vs.VideoFormat, vs.PresetFormat]
HoldsPropValueT = Union[vs.FrameProps, vs.VideoFrame, vs.AudioFrame, vs.VideoNode, vs.AudioNode]

EnumFuncExceptT = str | tuple[Callable[..., Any] | str, str]  # type: ignore
FuncExceptT = str | Callable[..., Any] | tuple[Callable[..., Any] | str, str]  # type: ignore


class VSFunction(Protocol):
    def __call__(self, clip: vs.VideoNode, *args: Any, **kwargs: Any) -> vs.VideoNode:
        ...


StrArr = SingleOrArr[SupportsString]
StrArrOpt = SingleOrArrOpt[SupportsString]

PassthroughC = Callable[[F], F]


AnythingElse = TypeVar(
    'AnythingElse', bound=Union[
        type, int, str, None, SupportsFloatOrIndex, ByteData, SupportsAllComparisons,
        SupportsTrunc, SupportsString, SupportsRichComparison, VSFunction, ComparatorFunc, ByteString,
        SupportsDunderLT, SupportsDunderGT, SupportsDunderLE, SupportsDunderGE, Set, Mapping, Deque  # type: ignore
    ]
)


class ConstantFormatVideoNode(vs.VideoNode):
    format: vs.VideoFormat
