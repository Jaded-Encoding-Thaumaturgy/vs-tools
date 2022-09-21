from __future__ import annotations

import sys
from copy import deepcopy
from typing import Any, Iterator, TypeVar

from ..types import MISSING

from ..types import FuncExceptT, Self, SupportsString

__all__ = [
    'CustomError',

    'CustomValueError',
    'CustomIndexError',
    'CustomOverflowError',
    'CustomKeyError',
    'CustomTypeError',
    'CustomRuntimeError',
    'CustomPermissionError'
]


class CustomErrorMeta(type):
    """Custom base exception meta class."""

    def __new__(cls: type[Self], *args: Any) -> Self:
        obj = type.__new__(cls, *args)

        if obj.__qualname__.startswith('Custom'):  # type: ignore
            obj.__qualname__ = obj.__qualname__[6:]  # type: ignore

        if sys.stdout.isatty():
            obj.__qualname__ = f'\033[0;31;1m{obj.__qualname__}\033[0m'  # type: ignore

        obj.__module__ = Exception.__module__

        return obj


class CustomError(Exception, metaclass=CustomErrorMeta):
    """Custom base exception class."""

    def __init__(
        self, message: SupportsString | None = None, func: FuncExceptT | None = None, **kwargs: Any
    ) -> None:
        self.message = message
        self.func = func
        self.kwargs = kwargs

        super().__init__(message)

    def __call__(
        self: SelfError, message: SupportsString | None = MISSING, func: FuncExceptT | None = MISSING, **kwargs: Any
    ) -> SelfError:
        err = deepcopy(self)

        if message is not MISSING:
            err.message = message

        if func is not MISSING:
            err.func = func

        return err

    def __str__(self) -> str:
        from ..functions import norm_func_name

        message = self.message

        if message is self.func is None:
            return super().__init__()
        elif not message:
            message = 'An error occurred!'

        func_header = norm_func_name(self.func).strip() if self.func else 'Unknown'

        if sys.stdout.isatty():
            func_header = f'\033[0;36m{func_header}\033[0m'

        func_header = f'({func_header})'

        kwargs = self.kwargs.copy()

        if kwargs:
            kwargs = {
                key: (
                    ', '.join(norm_func_name(v) for v in value)
                    if isinstance(value, Iterator) else
                    norm_func_name(value)
                ) for key, value in kwargs.items()
            }

        return f'{func_header} {self.message!s}'.format(**kwargs)


SelfError = TypeVar('SelfError', bound=CustomError)


class CustomValueError(CustomError, ValueError):
    """Custom base ValueError class."""


class CustomIndexError(CustomError, IndexError):
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""


class CustomOverflowError(CustomError, OverflowError):
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""


class CustomKeyError(CustomError, KeyError):
    """Custom base KeyError class."""


class CustomTypeError(CustomError, TypeError):
    """Custom base TypeError class."""


class CustomRuntimeError(CustomError, RuntimeError):
    """Custom base RuntimeError class."""


class CustomPermissionError(CustomError, PermissionError):
    """Custom base PermissionError class."""
