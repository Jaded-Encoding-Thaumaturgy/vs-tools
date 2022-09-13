from __future__ import annotations

from typing import Any, Callable, Protocol, Sequence, Union

import vapoursynth as vs

from .builtins import F, SingleOrArr, SingleOrArrOpt, SupportsString

__all__ = [
    'MissingT', 'MISSING',

    'FuncExceptT', 'EnumFuncExceptT',

    'VideoPropT',

    'VideoFormatT',

    'HoldsVideoFormatT', 'HoldsPropValueT',

    'VSFunction',

    'StrArr', 'StrArrOpt',

    'PassthroughC',

    'ConstantFormatVideoNode'
]


class MissingT:
    ...


MISSING = MissingT()

# TODO update with types from vsrepo PR#186
VideoPropT = Union[
    int, Sequence[int],
    float, Sequence[float],
    str, Sequence[str],
    vs.VideoNode, Sequence[vs.VideoNode],
    vs.VideoFrame, Sequence[vs.VideoFrame],
    Callable[..., Any], Sequence[Callable[..., Any]]
]
"""@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""

VideoFormatT = Union[int, vs.PresetFormat, vs.VideoFormat]
"""@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""

# TODO change to | when mypy fixes bug upstream
HoldsVideoFormatT = Union[vs.VideoNode, vs.VideoFrame, vs.VideoFormat, vs.PresetFormat]
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


StrArr = SingleOrArr[SupportsString]
StrArrOpt = SingleOrArrOpt[SupportsString]

PassthroughC = Callable[[F], F]


class ConstantFormatVideoNode(vs.VideoNode):
    format: vs.VideoFormat
