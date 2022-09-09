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

    class FileTypeBase(FileTypeIndexBase, CustomStrEnum):
        ...

    class FileTypeIndex(FileType):  # type: ignore
        def __call__(self, file_type: str | FileType) -> FileTypeIndexWithType:
            ...

    class FileTypeIndexWithType(FileTypeIndex):  # type: ignore
        file_type: FileType
else:
    FileTypeBase = CustomStrEnum
    FileTypeIndex = CustomStrEnum
    FileTypeIndexWithType = CustomStrEnum
