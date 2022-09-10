from __future__ import annotations

from io import BufferedRandom, BufferedReader, BufferedWriter, FileIO, TextIOWrapper
from os import F_OK, R_OK, W_OK, X_OK, access
from pathlib import Path
from typing import IO, Any, BinaryIO, Literal, overload

from ..exceptions import FileIsADirectoryError, FileNotExistsError, FilePermissionError, FileWasNotFoundError
from ..types import (
    FileOpener, FilePathType, FuncExceptT, OpenBinaryMode, OpenBinaryModeReading, OpenBinaryModeUpdating,
    OpenBinaryModeWriting, OpenTextMode
)

__all__ = [
    'check_perms',
    'open_file'
]


def check_perms(
    file: FilePathType, mode: OpenTextMode | OpenBinaryMode, *, func: FuncExceptT | None = None
) -> bool:
    """
    Confirm whether the user has write/read access to a file.

    :param file:                    Path to file.
    :param mode:                    Read/Write mode.
    :param func:                    @@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS

    :param:                         True if the user has write/read access, else False.

    :raises FileNotExistsError:     File could not be found.
    :raises FilePermissionError:    User does not have access to the file.
    :raises FileIsADirectoryError:  Given path is a directory, not a file.
    :raises FileWasNotFoundError:   Parent directories exist, but the given file could not be found.
    """
    file = Path(str(file))
    got_perms = False

    mode_i = F_OK

    if func is not None:
        if not str(file):
            raise FileNotExistsError(file, func)

    for char in 'rbU':
        mode_str = mode.replace(char, '')

    if file.is_file():
        if not mode_str:
            mode_i = R_OK
        elif 'x' in mode_str:
            mode_i = X_OK
        elif '+' in mode_str or 'w' in mode_str:
            mode_i = W_OK

        got_perms = access(file, mode_i)

    if func is not None:
        if not got_perms:
            raise FilePermissionError(file, func)
        elif file.is_dir():
            raise FileIsADirectoryError(file, func)
        elif not file.exists():
            if file.parent.exists():
                raise FileWasNotFoundError(file, func)
            else:
                raise FileNotExistsError(file, func)

    return got_perms


@overload
def open_file(
    file: FilePathType, mode: OpenTextMode = 'r+', buffering: int = ...,
    encoding: str | None = None, errors: str | None = ..., newline: str | None = ...,
    closefd: bool = ..., opener: FileOpener | None = ..., *, func: FuncExceptT | None = None
) -> TextIOWrapper:
    ...


@overload
def open_file(
    file: FilePathType, mode: OpenBinaryMode, buffering: Literal[0],
    encoding: None = None, errors: None = None, newline: None = ...,
    closefd: bool = ..., opener: FileOpener | None = ..., *, func: FuncExceptT | None = None
) -> FileIO:
    ...


@overload
def open_file(
    file: FilePathType, mode: OpenBinaryModeUpdating, buffering: Literal[-1, 1] = ...,
    encoding: None = None, errors: None = None, newline: None = ...,
    closefd: bool = ..., opener: FileOpener | None = ..., *, func: FuncExceptT | None = None
) -> BufferedRandom:
    ...


@overload
def open_file(
    file: FilePathType, mode: OpenBinaryModeWriting, buffering: Literal[-1, 1] = ...,
    encoding: None = None, errors: None = None, newline: None = ...,
    closefd: bool = ..., opener: FileOpener | None = ..., *, func: FuncExceptT | None = None
) -> BufferedWriter:
    ...


@overload
def open_file(
    file: FilePathType, mode: OpenBinaryModeReading, buffering: Literal[-1, 1] = ...,
    encoding: None = None, errors: None = None, newline: None = ...,
    closefd: bool = ..., opener: FileOpener | None = ..., *, func: FuncExceptT | None = None
) -> BufferedReader:
    ...


@overload
def open_file(
    file: FilePathType, mode: OpenBinaryMode, buffering: int = ...,
    encoding: None = None, errors: None = None, newline: None = ...,
    closefd: bool = ..., opener: FileOpener | None = ..., *, func: FuncExceptT | None = None
) -> BinaryIO:
    ...


@overload
def open_file(
    file: FilePathType, mode: str, buffering: int = ...,
    encoding: str | None = ..., errors: str | None = ..., newline: str | None = ...,
    closefd: bool = ..., opener: FileOpener | None = ..., *, func: FuncExceptT | None = None
) -> IO[Any]:
    ...


def open_file(file: FilePathType, mode: Any = 'r+', *args: Any, func: FuncExceptT | None = None, **kwargs: Any) -> Any:
    """
    Open a file.

    :param file:            Path to file.
    :param mode:            Writing mode.
    :param *args:           Positional Arguments to pass to ``open``.
    :param **kwargs:        Keyword Arguments to pass to ``open``.

    :return:                Opened file.
    """
    check_perms(file, mode, func=func)
    return open(file, mode, *args, **kwargs)
