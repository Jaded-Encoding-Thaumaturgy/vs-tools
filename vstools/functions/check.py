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
                raise error(function=function)

        if not only_first:
            for name, param in inspect.signature(function).parameters.items():
                if param.default is not inspect.Parameter.empty and _check(param.default):
                    raise error(
                        message=f'Variable-{vname} clip not allowed in default argument `{name}`.', function=function
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
    """
    Decorator for disallowing clips with variable formats.

    :param only_first:              Only verify the format of the first argument.
                                    Default: False.

    :raises VariableFormatError:    A clip with a variable format is found.
    """
    if function is None:
        return cast(Callable[[F], F], partial(disallow_variable_format, only_first=only_first))

    return _check_variable(
        function, 'format', VariableFormatError, only_first, lambda x: x.format is None
    )


@overload
def disallow_variable_resolution(*, only_first: bool = False) -> Callable[[F], F]:
    ...


@overload
def disallow_variable_resolution(function: F | None = None, /) -> F:
    ...


def disallow_variable_resolution(function: F | None = None, /, *, only_first: bool = False) -> Callable[[F], F] | F:
    """
    Decorator for disallowing clips with variable resolutions.

    :param only_first:                  Only verify the resolution of the first argument.
                                        Default: False.

    :raises VariableResolutionError:    A clip with a variable resolution is found.
    """
    if function is None:
        return cast(Callable[[F], F], partial(disallow_variable_resolution, only_first=only_first))

    return _check_variable(
        function, 'format', VariableResolutionError, only_first, lambda x: not all({x.width, x.height})
    )


@disallow_variable_format
@disallow_variable_resolution
def check_ref_clip(src: vs.VideoNode, ref: vs.VideoNode | None) -> None:
    """
    Decorator for ensuring the ref clip's format matches that of the input clip.

    If no ref clip can be found, this decorator will simply do nothing.

    :param src:     Input clip.
    :param ref:     Reference clip.
                    Default: None.

    :raises AssertionError:                     The format of either clip is None.
    :raises FormatsRefClipMismatchError:        The formats of the two clips do not match.
    :raises ResolutionsRefClipMismatchError:    The resolutions of the two clips do not match.
    """
    if ref is None:
        return

    assert src.format and ref.format

    if ref.format.id != src.format.id:
        raise FormatsRefClipMismatchError(check_ref_clip)

    if ref.width != src.width or ref.height != src.height:
        raise ResolutionsRefClipMismatchError(check_ref_clip)


def check_variable_format(clip: vs.VideoNode, function: FuncExceptT) -> TypeGuard[ConstantFormatVideoNode]:
    """
    Check for variable format and return an error if found.

    :raises VariableFormatError:    The clip is of a variable format.
    """
    if clip.format is None:
        raise VariableFormatError(function)

    return True


def check_variable_resolution(clip: vs.VideoNode, function: FuncExceptT) -> None:
    """
    Check for variable width or height and return an error if found.

    :raises VariableResolutionError:    The clip has a variable resolution.
    """
    if 0 in (clip.width, clip.height):
        raise VariableResolutionError(function)


def check_variable(clip: vs.VideoNode, function: FuncExceptT) -> TypeGuard[ConstantFormatVideoNode]:
    """
    Check for variable format and a variable resolution and return an error if found.

    :raises VariableFormatError:        The clip is of a variable format.
    :raises VariableResolutionError:    The clip has a variable resolution.
    """
    check_variable_format(clip, function)
    check_variable_resolution(clip, function)

    return True
