from __future__ import annotations

from stgpytools import (
    FileDescriptor, FileOpener, FilePathType, OpenBinaryMode, OpenBinaryModeReading, OpenBinaryModeUpdating,
    OpenBinaryModeWriting, OpenTextMode, OpenTextModeReading, OpenTextModeUpdating, OpenTextModeWriting, SPath,
    SPathLike
)

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

    'SPath', 'SPathLike',

    'DEP_URL'
]

DEP_URL = str
"""A string representing a URL to download a dependency from."""
