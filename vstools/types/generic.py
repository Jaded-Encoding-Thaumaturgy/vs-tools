from __future__ import annotations

from typing import Any, Callable, Protocol, TypeVar, Union

import vapoursynth as vs

from .builtins import F, SingleOrArr, SingleOrArrOpt, SupportsString

__all__ = [
    'MissingT', 'MISSING',

    'FuncExceptT', 'EnumFuncExceptT',

    'DataType', 'VSMapValue', 'BoundVSMapValue', 'VSMapValueCallback',

    'VideoFormatT',

    'HoldsVideoFormatT', 'HoldsPropValueT',

    'VSFunction', 'GenericVSFunction',

    'StrArr', 'StrArrOpt',

    'PassthroughC',

    'ConstantFormatVideoNode'
]


class MissingT:
    ...


MISSING = MissingT()


DataType = Union[str, bytes, bytearray, SupportsString]

VSMapValue = Union[
    SingleOrArr[int],
    SingleOrArr[float],
    SingleOrArr[DataType],
    SingleOrArr[vs.VideoNode],
    SingleOrArr[vs.VideoFrame],
    SingleOrArr[vs.AudioNode],
    SingleOrArr[vs.AudioFrame],
    SingleOrArr['VSMapValueCallback[Any]']
]
"""@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""

BoundVSMapValue = TypeVar('BoundVSMapValue', bound=VSMapValue)
"""@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""

VSMapValueCallback = Callable[..., BoundVSMapValue]
"""@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""

VideoFormatT = Union[vs.PresetFormat, vs.VideoFormat]
"""@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""

# TODO change to | when mypy fixes bug upstream
HoldsVideoFormatT = Union[vs.VideoNode, vs.VideoFrame, vs.VideoFormat]
"""@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""

HoldsPropValueT = Union[vs.FrameProps, vs.VideoFrame, vs.AudioFrame, vs.VideoNode, vs.AudioNode]
"""@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""

EnumFuncExceptT = str | tuple[Callable[..., Any] | str, str]  # type: ignore
"""@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""

FuncExceptT = str | Callable[..., Any] | tuple[Callable[..., Any] | str, str]  # type: ignore
"""@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""


class VSFunction(Protocol):
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""

    def __call__(self, clip: vs.VideoNode, *args: Any, **kwargs: Any) -> vs.VideoNode:
        ...


GenericVSFunction = Callable[..., vs.VideoNode]


StrArr = SingleOrArr[SupportsString]
StrArrOpt = SingleOrArrOpt[SupportsString]

PassthroughC = Callable[[F], F]


class ConstantFormatVideoNode(vs.VideoNode):
    format: vs.VideoFormat
