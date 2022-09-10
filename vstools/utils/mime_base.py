from __future__ import annotations

from typing import TYPE_CHECKING

from ..enums import CustomStrEnum

__all__ = [
    'FileTypeBase',
    'FileTypeIndex',
    'FileTypeIndexWithType'
]

if TYPE_CHECKING:
    from .mime import FileType

    class FileTypeIndexBase:
        """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""

        INDEX: FileTypeIndex

        ...

    class FileTypeBase(FileTypeIndexBase, CustomStrEnum):
        """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""

        ...

    class FileTypeIndex(FileType):  # type: ignore
        """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""

        def __call__(self, file_type: str | FileType) -> FileTypeIndexWithType:
            """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""

            ...

    class FileTypeIndexWithType(FileTypeIndex):  # type: ignore
        """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""

        file_type: FileType

        ...
else:
    FileTypeBase = CustomStrEnum
    FileTypeIndex = CustomStrEnum
    FileTypeIndexWithType = CustomStrEnum
