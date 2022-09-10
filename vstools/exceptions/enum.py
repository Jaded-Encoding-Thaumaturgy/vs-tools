from __future__ import annotations

from .base import CustomKeyError, CustomValueError

__all__ = [
    'UndefinedChromaLocationError',
    'UnsupportedChromaLocationError',
    'UndefinedFieldBasedError',
    'UnsupportedFieldBasedError',
    'NotFoundEnumValue'
]


class UndefinedChromaLocationError(CustomValueError):
    """Raised when an undefined chroma location is passed."""


class UnsupportedChromaLocationError(CustomValueError):
    """Raised when an unsupported chroma location is passed."""


class UndefinedFieldBasedError(CustomValueError):
    """Raised when an undefined field type is passed."""


class UnsupportedFieldBasedError(CustomValueError):
    """Raised when an unsupported field type is passed."""


class NotFoundEnumValue(CustomKeyError):
    """Raised when you try to instantiate an Enum with unkown value"""
