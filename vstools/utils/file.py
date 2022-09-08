from __future__ import annotations

from io import BufferedRandom, BufferedReader, BufferedWriter, FileIO, TextIOWrapper
from os import F_OK, R_OK, W_OK, X_OK, access
from pathlib import Path
from typing import IO, Any, BinaryIO, Literal, overload

from ..enums import FuncExceptT
from ..exceptions import FileIsADirectoryError, FileNotExistsError, FilePermissionError, FileWasNotFoundError
from ..types import (
    FileDescriptor, FileOpener, FilePathType, OpenBinaryMode, OpenBinaryModeReading, OpenBinaryModeUpdating,
    OpenBinaryModeWriting, OpenTextMode
)

__all__ = [
    'check_perms',
    'open_file'
]


def check_perms(file: FilePathType | FileDescriptor, mode: OpenTextMode | OpenBinaryMode):
    mode_i = F_OK

    for char in 'rbU':
        mode = mode.replace(char, '')

    if not mode:
        mode_i = R_OK
    elif 'x' in mode:
        mode_i = X_OK
    elif '+' in mode or 'w' in mode:
        mode_i = W_OK

    return access(file, mode_i)


@overload
def open_file(
    file: FilePathType | FileDescriptor, mode: OpenTextMode = 'r+', buffering: int = ...,
    encoding: str | None = None, errors: str | None = ..., newline: str | None = ...,
    closefd: bool = ..., opener: FileOpener | None = ..., *, func: FuncExceptT | None = None
) -> TextIOWrapper:
    ...


@overload
def open_file(
    file: FilePathType | FileDescriptor, mode: OpenBinaryMode, buffering: Literal[0],
    encoding: None = None, errors: None = None, newline: None = ...,
    closefd: bool = ..., opener: FileOpener | None = ..., *, func: FuncExceptT | None = None
) -> FileIO:
    ...


@overload
def open_file(
    file: FilePathType | FileDescriptor, mode: OpenBinaryModeUpdating, buffering: Literal[-1, 1] = ...,
    encoding: None = None, errors: None = None, newline: None = ...,
    closefd: bool = ..., opener: FileOpener | None = ..., *, func: FuncExceptT | None = None
) -> BufferedRandom:
    ...


@overload
def open_file(
    file: FilePathType | FileDescriptor, mode: OpenBinaryModeWriting, buffering: Literal[-1, 1] = ...,
    encoding: None = None, errors: None = None, newline: None = ...,
    closefd: bool = ..., opener: FileOpener | None = ..., *, func: FuncExceptT | None = None
) -> BufferedWriter:
    ...


@overload
def open_file(
    file: FilePathType | FileDescriptor, mode: OpenBinaryModeReading, buffering: Literal[-1, 1] = ...,
    encoding: None = None, errors: None = None, newline: None = ...,
    closefd: bool = ..., opener: FileOpener | None = ..., *, func: FuncExceptT | None = None
) -> BufferedReader:
    ...


@overload
def open_file(
    file: FilePathType | FileDescriptor, mode: OpenBinaryMode, buffering: int = ...,
    encoding: None = None, errors: None = None, newline: None = ...,
    closefd: bool = ..., opener: FileOpener | None = ..., *, func: FuncExceptT | None = None
) -> BinaryIO:
    ...


@overload
def open_file(
    file: FilePathType | FileDescriptor, mode: str, buffering: int = ...,
    encoding: str | None = ..., errors: str | None = ..., newline: str | None = ...,
    closefd: bool = ..., opener: FileOpener | None = ..., *, func: FuncExceptT | None = None
) -> IO[Any]:
    ...


def open_file(
    file: FilePathType | FileDescriptor, mode: Any = 'r+',
    *args: Any, func: FuncExceptT | None = None, **kwargs: Any
) -> Any:
    if not isinstance(file, int):
        file = Path(str(file))

        if not str(file):
            raise FileNotExistsError(file, func)

        if file.is_file():
            if not check_perms(file, mode):
                raise FilePermissionError(file, func)
        elif file.is_dir():
            raise FileIsADirectoryError
        elif not file.exists():
            if file.parent.exists():
                raise FileWasNotFoundError(file, func)
            else:
                raise FileNotExistsError(file, func)

    return open(file, mode, *args, **kwargs)
