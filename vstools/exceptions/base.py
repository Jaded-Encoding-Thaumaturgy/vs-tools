from __future__ import annotations

from typing import Any

from ..types import F, SupportsString

__all__ = [
    'CustomError',

    'CustomValueError',
    'CustomKeyError',
    'CustomTypeError'
]


class CustomError(Exception):
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
            func_header = f'{func_name}: '
        else:
            func_header = ''

        super().__init__(f'{func_header}\'{formatted}\'')


class CustomValueError(ValueError, CustomError):
    ...


class CustomKeyError(KeyError, CustomError):
    ...


class CustomTypeError(TypeError, CustomError):
    ...
