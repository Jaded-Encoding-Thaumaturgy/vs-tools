from __future__ import annotations

import sys
from typing import Any

from .base import CustomError
from ..types import SupportsString, FuncExceptT


__all__ = [
    'CustomImportError',
    'DependencyNotFoundError'
]


class CustomImportError(CustomError, ImportError):
    """Raised when there's a general import error."""

    def __init__(
        self, func: FuncExceptT, package: str, message: SupportsString = "Import failed for package '{package}'!",
        **kwargs: Any
    ) -> None:
        super().__init__(message, func, package=package, **kwargs)


class DependencyNotFoundError(CustomImportError):
    """Raised when there's a missing optional dependency."""

    def __init__(
        self, func: FuncExceptT, package: str, reason: str | None = None,
        message: SupportsString = "Missing dependency '{package}'!",
        **kwargs: Any
    ) -> None:

        if reason:
            reason = f'({reason})'

            if sys.stdout and sys.stdout.isatty():
                reason = f'\033[0;33m{reason}\033[0m'

            message = f'{message} {reason}'

        super().__init__(func, package, message, **kwargs)
