from __future__ import annotations

from .base import CustomError, CustomPermissionError


__all__ = [
    'FileNotExistsError',
    'FileWasNotFoundError',
    'FilePermissionError',
    'FileTypeMismatchError',
    'FileIsADirectoryError'
]


class FileNotExistsError(CustomError, FileExistsError):
    """Raised when a file doesn't exists"""


class FileWasNotFoundError(CustomError, FileNotFoundError):
    """Raised when a file wasn't found but the path is correct, e.g. parent directory exists"""


class FilePermissionError(CustomPermissionError):
    """Raised when you try to access a file but haven't got permissions to do so"""


class FileTypeMismatchError(CustomError, OSError):
    """Raised when you try to access a file with a FileType != AUTO and it's another file type"""


class FileIsADirectoryError(CustomError, IsADirectoryError):
    """Raised when you try to access a file but it's a directory instead"""
