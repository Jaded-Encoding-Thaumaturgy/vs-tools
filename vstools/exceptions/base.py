from __future__ import annotations

import sys
from typing import Any

from ..types import F, Self, SupportsString

__all__ = [
    'CustomError',

    'CustomValueError',
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
        self, message: SupportsString | None = None, function: SupportsString | F | None = None, **kwargs: Any
    ) -> None:
        from ..functions import norm_func_name

        if message is None:
            return super().__init__()

        message = str(message)

        formatted = message.format(**kwargs)

        if function:
            func_name = norm_func_name(function)
            func_header = f'({func_name})'

            if sys.stdout.isatty():
                func_header = f'\033[0;36m{func_header}\033[0m'

            func_header += ' '
        else:
            func_header = ''

        super().__init__(func_header + formatted)


class CustomValueError(CustomError, ValueError):
    """Custom base ValueError class."""

    ...


class CustomKeyError(CustomError, KeyError):
    """Custom base KeyError class."""

    ...


class CustomTypeError(CustomError, TypeError):
    """Custom base TypeError class."""

    ...


class CustomRuntimeError(CustomError, RuntimeError):
    """Custom base RuntimeError class."""

    ...


class CustomPermissionError(CustomError, PermissionError):
    """Custom base PermissionError class."""

    ...
