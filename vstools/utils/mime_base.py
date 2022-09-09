from __future__ import annotations

from typing import TYPE_CHECKING

from ..enums import CustomStrEnum

__all__ = [
    'FileTypeBase'
]

if TYPE_CHECKING:
    from .mime import FileType

    class FileTypeIndexBase:
        INDEX: FileTypeIndex

    class FileTypeBase(FileTypeIndexBase, CustomStrEnum):
        ...

    class FileTypeIndex(FileType):
        def __call__(self, file_type: str | FileType) -> FileTypeIndexWithType:
            ...

    class FileTypeIndexWithType(FileTypeIndex):
        file_type: FileType
else:
    FileTypeBase = CustomStrEnum
    FileTypeIndexWithType = CustomStrEnum
