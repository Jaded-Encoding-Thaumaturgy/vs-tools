from __future__ import annotations

from os import PathLike, path
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Iterable, Literal, TypeAlias, Union

__all__ = [
    'FilePathType', 'FileDescriptor',
    'FileOpener',

    'OpenTextModeUpdating',
    'OpenTextModeWriting',
    'OpenTextModeReading',

    'OpenBinaryModeUpdating',
    'OpenBinaryModeWriting',
    'OpenBinaryModeReading',

    'OpenTextMode',
    'OpenBinaryMode',

    'SPath', 'SPathLike'
]

FileDescriptor: TypeAlias = int

FilePathType: TypeAlias = str | bytes | PathLike[str] | PathLike[bytes]

FileOpener: TypeAlias = Callable[[str, int], int]

OpenTextModeUpdating: TypeAlias = Literal[
    'r+', '+r', 'rt+', 'r+t', '+rt', 'tr+', 't+r', '+tr', 'w+', '+w', 'wt+', 'w+t', '+wt', 'tw+', 't+w', '+tw',
    'a+', '+a', 'at+', 'a+t', '+at', 'ta+', 't+a', '+ta', 'x+', '+x', 'xt+', 'x+t', '+xt', 'tx+', 't+x', '+tx',
]
OpenTextModeWriting: TypeAlias = Literal[
    'w', 'wt', 'tw', 'a', 'at', 'ta', 'x', 'xt', 'tx'
]
OpenTextModeReading: TypeAlias = Literal[
    'r', 'rt', 'tr', 'U', 'rU', 'Ur', 'rtU', 'rUt', 'Urt', 'trU', 'tUr', 'Utr'
]

OpenBinaryModeUpdating: TypeAlias = Literal[
    'rb+', 'r+b', '+rb', 'br+', 'b+r', '+br', 'wb+', 'w+b', '+wb', 'bw+', 'b+w', '+bw',
    'ab+', 'a+b', '+ab', 'ba+', 'b+a', '+ba', 'xb+', 'x+b', '+xb', 'bx+', 'b+x', '+bx'
]
OpenBinaryModeWriting: TypeAlias = Literal[
    'wb', 'bw', 'ab', 'ba', 'xb', 'bx'
]
OpenBinaryModeReading: TypeAlias = Literal[
    'rb', 'br', 'rbU', 'rUb', 'Urb', 'brU', 'bUr', 'Ubr'
]

OpenTextMode: TypeAlias = OpenTextModeUpdating | OpenTextModeWriting | OpenTextModeReading
OpenBinaryMode: TypeAlias = OpenBinaryModeUpdating | OpenBinaryModeReading | OpenBinaryModeWriting


class SPath(Path):
    """Modified version of pathlib.Path"""
    _flavour = type(Path())._flavour  # type: ignore

    if TYPE_CHECKING:
        def __new__(cls, *args: SPathLike, **kwargs: Any) -> SPath:
            ...

    def format(self, *args: Any, **kwargs: Any) -> SPath:
        return SPath(self.to_str().format(*args, **kwargs))

    def to_str(self) -> str:
        return str(self)

    def get_folder(self) -> SPath:
        folder_path = self.resolve()

        if folder_path.is_dir():
            return folder_path

        return SPath(path.dirname(folder_path))

    def mkdirp(self) -> None:
        return self.get_folder().mkdir(parents=True, exist_ok=True)

    def rmdirs(self, missing_ok: bool = False, ignore_errors: bool = True) -> None:
        from shutil import rmtree

        try:
            return rmtree(str(self.get_folder()), ignore_errors)
        except FileNotFoundError:
            if not missing_ok:
                raise

    def read_lines(
        self, encoding: str | None = None, errors: str | None = None, keepends: bool = False
    ) -> list[str]:
        return super().read_text(encoding, errors).splitlines(keepends)

    def write_lines(
        self, data: Iterable[str], encoding: str | None = None,
        errors: str | None = None, newline: str | None = None
    ) -> int:
        return super().write_text('\n'.join(data), encoding, errors, newline)


SPathLike = Union[str, Path, SPath]
