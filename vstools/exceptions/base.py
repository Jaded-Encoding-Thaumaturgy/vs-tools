from __future__ import annotations

import sys
from typing import Any

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
        self, message: SupportsString | None = None, function: FuncExceptT | None = None, **kwargs: Any
    ) -> None:
        """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
        from ..functions import norm_func_name

        if message is None:
            if function is None:
                return super().__init__()

            message = 'An error occurred!'

        message = str(message)

        if function:
            func_name = norm_func_name(function)
            func_header = f'({func_name})'

            if sys.stdout.isatty():
                func_header = f'\033[0;36m{func_header}\033[0m'

            func_header += ' '
        else:
            func_header = ''

        if kwargs:
            kwargs = {key: norm_func_name(value) for key, value in kwargs.items()}

        super().__init__((func_header + message).format(**kwargs))


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
