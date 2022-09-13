from __future__ import annotations
from typing import Any

from ..types import FuncExceptT
from .base import CustomPermissionError, CustomValueError

__all__ = [
    'UndefinedMatrixError',
    'UndefinedTransferError',
    'UndefinedPrimariesError',

    'ReservedMatrixError',
    'ReservedTransferError',
    'ReservedPrimariesError',

    'InvalidMatrixError',
    'InvalidTransferError',
    'InvalidPrimariesError',

    'UnsupportedMatrixError',
    'UnsupportedTransferError',
    'UnsupportedPrimariesError',
    'UnsupportedColorRangeError'
]

########################################################
# Matrix


class UndefinedMatrixError(CustomValueError):
    """Raised when an undefined matrix is passed."""


class ReservedMatrixError(CustomPermissionError):
    """Raised when a reserved matrix is requested."""


class UnsupportedMatrixError(CustomValueError):
    """Raised when an unsupported matrix is passed."""


class InvalidMatrixError(CustomValueError):
    """Raised when an invalid matrix is passed."""

    def __init__(
        self, function: FuncExceptT, matrix: int = 2, message: str = 'You can\'t set a matrix of {matrix}!',
        **kwargs: Any
    ) -> None:
        """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
        super().__init__(message, function, matrix=matrix, **kwargs)


########################################################
# Transfer

class UndefinedTransferError(CustomValueError):
    """Raised when an undefined transfer is passed."""


class ReservedTransferError(CustomPermissionError):
    """Raised when a reserved transfer is requested."""


class UnsupportedTransferError(CustomValueError):
    """Raised when an unsupported transfer is passed."""


class InvalidTransferError(CustomValueError):
    """Raised when an invalid matrix is passed."""

    def __init__(
        self, function: FuncExceptT, transfer: int = 2, message: str = 'You can\'t set a transfer of {transfer}!',
        **kwargs: Any
    ) -> None:
        """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
        super().__init__(message, function, transfer=transfer, **kwargs)


########################################################
# Primaries

class UndefinedPrimariesError(CustomValueError):
    """Raised when an undefined primaries value is passed."""


class ReservedPrimariesError(CustomPermissionError):
    """Raised when reserved primaries are requested."""


class UnsupportedPrimariesError(CustomValueError):
    """Raised when a unsupported primaries value is passed."""


class InvalidPrimariesError(CustomValueError):
    """Raised when an invalid matrix is passed."""

    def __init__(
        self, function: FuncExceptT, primaries: int = 2, message: str = 'You can\'t set primaries of {primaries}!',
        **kwargs: Any
    ) -> None:
        """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
        super().__init__(message, function, primaries=primaries, **kwargs)


########################################################
# ColorRange

class UnsupportedColorRangeError(CustomValueError):
    """Raised when a unsupported color range value is passed."""
