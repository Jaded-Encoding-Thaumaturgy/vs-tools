from __future__ import annotations

from typing import Any

from ..types import FuncExceptT, SupportsString
from .base import CustomError

__all__ = [
    'CustomImportError',
    'DependencyNotFoundError'
]


class CustomImportError(CustomError, ImportError):
    """Raised when there's a general import error."""

    def __init__(
        self, func: FuncExceptT, package: str | ImportError,
        message: SupportsString = "Import failed for package '{package}'!",
        **kwargs: Any
    ) -> None:
        """
        :param func:        Function this error was raised from.
        :param package:     Either the raised error or the name of the missing package.
        :param message:     Custom error message.
        """

        super().__init__(message, func, package=package if isinstance(package, str) else package.name, **kwargs)


class DependencyNotFoundError(CustomImportError):
    """Raised when there's a missing optional dependency."""

    def __init__(
        self, func: FuncExceptT, package: str | ImportError,
        message: SupportsString = "Missing dependency '{package}'!",
        **kwargs: Any
    ) -> None:
        super().__init__(func, package, message, **kwargs)
