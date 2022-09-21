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
"""Values that a VSMap can hold, so all that a :py:attr:`vs.Function`` can accept in args and can return."""

BoundVSMapValue = TypeVar('BoundVSMapValue', bound=VSMapValue)
"""Type variable that can be one of the types in a VSMapValue."""

VSMapValueCallback = Callable[..., BoundVSMapValue]
"""Callback that can be held in a VSMap. It can only return values representable in a VSMap."""

VideoFormatT = Union[vs.PresetFormat, vs.VideoFormat]
"""Types representing a clear VideoFormat."""

# TODO change to | when mypy fixes bug upstream
HoldsVideoFormatT = Union[vs.VideoNode, vs.VideoFrame, vs.VideoFormat]
"""Types from which a clear VideoFormat can be retrieved."""

HoldsPropValueT = Union[vs.FrameProps, vs.VideoFrame, vs.AudioFrame, vs.VideoNode, vs.AudioNode]
"""Types that can hold :py:attr:`vs.FrameProps`."""

FuncExceptT = str | Callable[..., Any] | tuple[Callable[..., Any] | str, str]  # type: ignore
"""
This type is used in specific functions that can throw an exception.
```
def can_throw(..., *, func: FuncExceptT) -> None:
    ...
    if some_error:
        raise CustomValueError('Some error occurred!!', func)

def some_func() -> None:
    ...
    can_throw(..., func=some_func)
```
If an error occurrs, this will print a clear error ->\n
``ValueError: (some_func) Some error occurred!!``
"""

EnumFuncExceptT = str | tuple[Callable[..., Any] | str, str]  # type: ignore
"""
:py:attr:`FuncExceptT` with a second argument that takes the name of the argument in the function.
```
def some_enum_usage(my_epic_matrix: MatrixT) -> None:
    ...
    some_matrix = Matrix.from_param(my_epic_matrix, (some_enum_usage, 'my_epic_matrix'))
    ...

some_enum_usage(999)
```
If an error occurs, this will print a clear error ->\n
NotFoundEnumValue: (some_enum_usage) Value for "my_epic_matrix" argument must be a valid Matrix.\n
It can be a value in [RGB (0), BT709 (1), ..., ICTCP (14)].
"""


class VSFunction(Protocol):
    """Function that takes a :py:attr:`vs.VideoNode` as its first argument and returns a :py:attr:`vs.VideoNode`."""

    def __call__(self, clip: vs.VideoNode, *args: Any, **kwargs: Any) -> vs.VideoNode:
        ...


GenericVSFunction = Callable[..., vs.VideoNode]


StrArr = SingleOrArr[SupportsString]
StrArrOpt = SingleOrArrOpt[SupportsString]

PassthroughC = Callable[[F], F]


class ConstantFormatVideoNode(vs.VideoNode):
    format: vs.VideoFormat
