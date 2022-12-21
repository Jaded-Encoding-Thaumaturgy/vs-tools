from __future__ import annotations

import sys
from copy import deepcopy
from typing import TYPE_CHECKING, Any, TypeVar

from ..types import MISSING, FuncExceptT, SupportsString

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


if TYPE_CHECKING:
    class ExceptionT(Exception, type):
        ...
else:
    ExceptionT = Exception


class CustomErrorMeta(type):
    def __new__(cls: type[SelfCErrorMeta], *args: Any) -> SelfCErrorMeta:
        return CustomErrorMeta.setup_exception(type.__new__(cls, *args))  # type: ignore

    @staticmethod
    def setup_exception(exception: SelfCErrorMeta, override: str | ExceptionT | None = None) -> SelfCErrorMeta:
        if override:
            if isinstance(override, str):
                over_name = over_qual = override
            else:
                over_name, over_qual = override.__name__, override.__qualname__

            if over_name.startswith('Custom'):
                exception.__name__ = over_name
            else:
                exception.__name__ = f'Custom{over_name}'

            exception.__qualname__ = over_qual

        if exception.__qualname__.startswith('Custom'):
            exception.__qualname__ = exception.__qualname__[6:]

        if sys.stdout and sys.stdout.isatty():
            exception.__qualname__ = f'\033[0;31;1m{exception.__qualname__}\033[0m'

        exception.__module__ = Exception.__module__

        return exception

    if TYPE_CHECKING:
        def __getitem__(self, exception: type[Exception]) -> CustomError:
            ...


SelfCErrorMeta = TypeVar('SelfCErrorMeta', bound=CustomErrorMeta)


class CustomError(ExceptionT, metaclass=CustomErrorMeta):
    def __init__(
        self, message: SupportsString | None = None, func: FuncExceptT | None = None, reason: Any = None, **kwargs: Any
    ) -> None:
        self.message = message
        self.func = func
        self.reason = reason
        self.kwargs = kwargs

        super().__init__(message)

    def __class_getitem__(cls, exception: str | type[ExceptionT] | ExceptionT) -> CustomError:
        if isinstance(exception, str):
            class inner_exception(cls):  # type: ignore
                ...
        else:
            if not issubclass(exception, type):
                exception = exception.__class__

            class inner_exception(cls, exception):  # type: ignore
                ...

        return CustomErrorMeta.setup_exception(inner_exception, exception)  # type: ignore

    def __call__(
        self: SelfError, message: SupportsString | None = MISSING,
        func: FuncExceptT | None = MISSING, reason: SupportsString | FuncExceptT | None = MISSING,  # type: ignore
        **kwargs: Any
    ) -> SelfError:
        err = deepcopy(self)

        if message is not MISSING:
            err.message = message

        if func is not MISSING:  # type: ignore[comparison-overlap]
            err.func = func

        if reason is not MISSING:
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
            reason = norm_display_name(self.reason)

            if not isinstance(self.reason, dict):
                reason = f'({reason})'

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
