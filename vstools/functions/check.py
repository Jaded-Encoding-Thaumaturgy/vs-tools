from __future__ import annotations

import inspect
from functools import partial, wraps
from typing import Any, Callable, TypeGuard, cast, overload

import vapoursynth as vs

from ..exceptions import (
    CustomError, FormatsRefClipMismatchError, ResolutionsRefClipMismatchError, VariableFormatError,
    VariableResolutionError
)
from ..types import ConstantFormatVideoNode, F, FuncExceptT

__all__ = [
    'disallow_variable_format',
    'disallow_variable_resolution',
    'check_ref_clip',
    'check_variable_format',
    'check_variable_resolution',
    'check_variable'
]


def _check_variable(
    function: F, vname: str, error: type[CustomError],
    only_first: bool, check_func: Callable[[vs.VideoNode], bool]
) -> F:
    def _check(x: Any) -> bool:
        return isinstance(x, vs.VideoNode) and check_func(x)

    @wraps(function)
    def _wrapper(*args: Any, **kwargs: Any) -> Any:
        for obj in args[:1] if only_first else [*args, *kwargs.values()]:
            if _check(obj):
                raise error(func=function)

        if not only_first:
            for name, param in inspect.signature(function).parameters.items():
                if param.default is not inspect.Parameter.empty and _check(param.default):
                    raise error(
                        message=f'Variable-{vname} clip not allowed in default argument `{name}`.', func=function
                    )

        return function(*args, **kwargs)

    return cast(F, _wrapper)


@overload
def disallow_variable_format(*, only_first: bool = False) -> Callable[[F], F]:
    ...


@overload
def disallow_variable_format(function: F | None = None, /) -> F:
    ...


def disallow_variable_format(function: F | None = None, /, *, only_first: bool = False) -> Callable[[F], F] | F:
    if function is None:
        return cast(Callable[[F], F], partial(disallow_variable_format, only_first=only_first))

    return _check_variable(
        function, 'format', VariableFormatError, only_first, lambda x: x.format is None
    )


@overload
def disallow_variable_resolution(*, only_first: bool = False) -> Callable[[F], F]:
    ...


@overload
def disallow_variable_resolution(func: F | None = None, /) -> F:
    ...


def disallow_variable_resolution(function: F | None = None, /, *, only_first: bool = False) -> Callable[[F], F] | F:
    if function is None:
        return cast(Callable[[F], F], partial(disallow_variable_resolution, only_first=only_first))

    return _check_variable(
        function, 'resolution', VariableResolutionError, only_first, lambda x: not all({x.width, x.height})
    )


@disallow_variable_format
@disallow_variable_resolution
def check_ref_clip(src: vs.VideoNode, ref: vs.VideoNode | None, func: FuncExceptT | None = None) -> None:
    from .funcs import fallback

    if ref is None:
        return

    func = fallback(func, check_ref_clip)  # type: ignore

    assert check_variable(src, func)  # type: ignore
    assert check_variable(ref, func)  # type: ignore

    if ref.format.id != src.format.id:
        raise FormatsRefClipMismatchError(func)  # type: ignore

    if ref.width != src.width or ref.height != src.height:
        raise ResolutionsRefClipMismatchError(func)  # type: ignore


def check_variable_format(clip: vs.VideoNode, func: FuncExceptT) -> TypeGuard[ConstantFormatVideoNode]:
    """
    Check for variable format and return an error if found.
    :raises VariableFormatError:    The clip is of a variable format.
    """
    if clip.format is None:
        raise VariableFormatError(func)

    return True


def check_variable_resolution(clip: vs.VideoNode, func: FuncExceptT) -> None:
    """
    Check for variable width or height and return an error if found.
    :raises VariableResolutionError:    The clip has a variable resolution.
    """
    if 0 in (clip.width, clip.height):
        raise VariableResolutionError(func)


def check_variable(clip: vs.VideoNode, func: FuncExceptT) -> TypeGuard[ConstantFormatVideoNode]:
    """
    Check for variable format and a variable resolution and return an error if found.
    :raises VariableFormatError:        The clip is of a variable format.
    :raises VariableResolutionError:    The clip has a variable resolution.
    """
    check_variable_format(clip, func)
    check_variable_resolution(clip, func)

    return True
