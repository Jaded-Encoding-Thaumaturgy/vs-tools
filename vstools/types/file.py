from __future__ import annotations

from os import PathLike
from typing import Callable, Literal, TypeAlias

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
    'OpenBinaryMode'
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

OpenTextMode: TypeAlias = OpenTextModeUpdating | OpenTextModeWriting | OpenTextModeReading  # type: ignore
OpenBinaryMode: TypeAlias = OpenBinaryModeUpdating | OpenBinaryModeReading | OpenBinaryModeWriting  # type: ignore
