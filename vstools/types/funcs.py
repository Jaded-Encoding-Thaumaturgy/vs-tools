from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterable, List, overload

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
        pass

    @string.getter
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
