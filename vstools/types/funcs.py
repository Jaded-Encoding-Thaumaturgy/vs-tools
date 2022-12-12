from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterable, List, SupportsIndex, overload

import vapoursynth as vs

from .builtins import SupportsString

__all__ = [
    'StrList'
]


class StrList(List[SupportsString]):
    if TYPE_CHECKING:
        @overload
        def __init__(self, __iterable: Iterable[SupportsString | None] = []) -> None:
            ...

        @overload
        def __init__(self, __iterable: Iterable[Iterable[SupportsString | None] | None] = []) -> None:
            ...

        def __init__(self, __iterable: Any = []) -> None:
            ...

    @property
    def string(self) -> str:
        return self.to_str()

    def to_str(self, ref: vs.VideoNode | None = None) -> str:
        if ref:
            raise NotImplementedError
        return str(self)

    def __str__(self) -> str:
        from ..functions import flatten

        return ' '.join(
            filter(
                None,
                (str(x).strip() for x in flatten(self) if x is not None)  # type: ignore[var-annotated,arg-type]
            )
        )

    def __add__(self, __x: list[SupportsString]) -> StrList:  # type: ignore[override]
        return StrList(super().__add__(__x))

    def __mul__(self, __n: SupportsIndex) -> StrList:
        return StrList(super().__mul__(__n))

    def __rmul__(self, __n: SupportsIndex) -> StrList:
        return StrList(super().__rmul__(__n))

    @property
    def mlength(self) -> int:
        return len(self) - 1

    def append(self, *__object: SupportsString) -> None:
        for __obj in __object:
            super().append(__obj)
