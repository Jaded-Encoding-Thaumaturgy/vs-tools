from __future__ import annotations
from functools import wraps

from typing import TYPE_CHECKING, Any, Callable, Iterable, List, SupportsIndex, TypeVar, overload

import vapoursynth as vs

from .builtins import T, SupportsString, P

__all__ = [
    'StrList',
    'Sentinel'
]


class StrList(List[SupportsString]):
    """Custom class for representing a recursively "stringable" list."""

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


class SentinelDispatcher:
    def check(self, ret_value: T, cond: bool) -> T | SentinelDispatcher:
        return ret_value if cond else self

    def check_cb(self, callback: Callable[P, tuple[T, bool]]) -> Callable[P, T | SentinelDispatcher]:
        @wraps(callback)
        def _wrap(*args: P.args, **kwargs: P.kwargs) -> T | SentinelDispatcher:
            return self.check(*callback(*args, **kwargs))

        return _wrap

    def filter(self: SelfSentinel, items: Iterable[T | SelfSentinel]) -> Iterable[T]:
        for item in items:
            if item is self:
                continue

            yield item  # type: ignore

    @classmethod
    def filter_multi(cls, items: Iterable[T | SelfSentinel], *sentinels: SelfSentinel) -> Iterable[T]:
        for item in items:
            if item in sentinels:
                continue

            yield item  # type: ignore

    def __getattr__(self, name: str) -> SentinelDispatcher:
        if name not in _sentinels:
            _sentinels[name] = SentinelDispatcher()
        return _sentinels[name]

    def __setattr__(self, __name: str, __value: Any) -> None:
        raise NameError

    def __call__(self) -> SentinelDispatcher:
        return SentinelDispatcher()


Sentinel = SentinelDispatcher()

_sentinels = dict[str, SentinelDispatcher]()

SelfSentinel = TypeVar('SelfSentinel', bound=SentinelDispatcher)
