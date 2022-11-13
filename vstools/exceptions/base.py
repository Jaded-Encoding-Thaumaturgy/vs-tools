from __future__ import annotations

import sys
from copy import deepcopy
from typing import TYPE_CHECKING, Any, TypeVar

from ..types import MISSING, FuncExceptT, Self, SupportsString

__all__ = [
    'CustomError',

    'CustomValueError',
    'CustomIndexError',
    'CustomOverflowError',
    'CustomKeyError',
    'CustomTypeError',
    'CustomRuntimeError',
    'CustomNotImplementedError',
    'CustomPermissionError'
]


class CustomErrorMeta(type):
    def __new__(cls: type[Self], *args: Any) -> Self:
        return CustomErrorMeta.setup_exception(type.__new__(cls, *args))

    @staticmethod
    def setup_exception(exception: Self, override: Exception | None = None) -> Self:
        if override:
            if override.__name__.startswith('Custom'):  # type: ignore
                exception.__name__ = override.__name__
            else:
                exception.__name__ = f'Custom{override.__name__}'

            exception.__qualname__ = override.__qualname__

        if exception.__qualname__.startswith('Custom'):  # type: ignore
            exception.__qualname__ = exception.__qualname__[6:]  # type: ignore

        if sys.stdout and sys.stdout.isatty():
            exception.__qualname__ = f'\033[0;31;1m{exception.__qualname__}\033[0m'  # type: ignore

        exception.__module__ = Exception.__module__

        return exception

    if TYPE_CHECKING:
        def __getitem__(self, exception: type[Exception]) -> CustomError:
            ...


class CustomError(Exception, metaclass=CustomErrorMeta):
    def __init__(
        self, message: SupportsString | None = None, func: FuncExceptT | None = None,
        reason: SupportsString | FuncExceptT | None = None, **kwargs: Any
    ) -> None:
        self.message = message
        self.func = func
        self.reason = reason
        self.kwargs = kwargs

        super().__init__(message)

    def __class_getitem__(cls, exception: type[Exception]) -> CustomError:
        class inner_exception(cls, exception):
            ...

        return type(cls).setup_exception(inner_exception, exception)

    def __call__(
        self: SelfError, message: SupportsString | None = MISSING,
        func: FuncExceptT | None = MISSING, reason: SupportsString | FuncExceptT | None = MISSING,
        **kwargs: Any
    ) -> SelfError:
        err = deepcopy(self)

        if message is not MISSING:
            err.message = message

        if func is not MISSING:  # type: ignore[comparison-overlap]
            err.func = func

        if reason is not MISSING:  # type: ignore[comparison-overlap]
            err.reason = reason

        err.kwargs |= kwargs

        return err

    def __str__(self) -> str:
        from ..functions import norm_display_name, norm_func_name

        message = self.message

        if not message:
            message = 'An error occurred!'

        if self.func:
            func_header = norm_func_name(self.func).strip()

            if sys.stdout and sys.stdout.isatty():
                func_header = f'\033[0;36m{func_header}\033[0m'

            func_header = f'({func_header}) '
        else:
            func_header = ''

        kwargs = self.kwargs.copy()

        if kwargs:
            kwargs = {
                key: norm_display_name(value) for key, value in kwargs.items()
            }

        if self.reason:
            reason = f'({norm_display_name(self.reason)})'

            if sys.stdout and sys.stdout.isatty():
                reason = f'\033[0;33m{reason}\033[0m'
            reason = f' {reason}'
        else:
            reason = ''

        return f'{func_header}{self.message!s}{reason}'.format(**kwargs).strip()


SelfError = TypeVar('SelfError', bound=CustomError)


class CustomValueError(CustomError, ValueError):
    ...


class CustomIndexError(CustomError, IndexError):
    ...


class CustomOverflowError(CustomError, OverflowError):
    ...


class CustomKeyError(CustomError, KeyError):
    ...


class CustomTypeError(CustomError, TypeError):
    ...


class CustomRuntimeError(CustomError, RuntimeError):
    ...


class CustomNotImplementedError(CustomError, NotImplementedError):
    ...


class CustomPermissionError(CustomError, PermissionError):
    ...
