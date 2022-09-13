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
        INDEX: FileTypeIndex
        """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""

    class FileTypeBase(FileTypeIndexBase, CustomStrEnum):
        ...

    class FileTypeIndex(FileType):  # type: ignore
        def __call__(self, file_type: str | FileType) -> FileTypeIndexWithType:
            """Instantiate FileType.INDEX with its own sub-FileType"""

    class FileTypeIndexWithType(FileTypeIndex):  # type: ignore
        """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
        file_type: FileType
else:
    FileTypeBase = CustomStrEnum
    FileTypeIndex = CustomStrEnum
    FileTypeIndexWithType = CustomStrEnum
