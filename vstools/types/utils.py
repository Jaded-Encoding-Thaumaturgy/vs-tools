from __future__ import annotations

from typing import Any, Callable, Concatenate, Generic, Protocol, cast, overload

from .builtins import F, P, R, T

__all__ = [
    'copy_signature',

    'inject_self'
]


class copy_signature(Generic[F]):
    def __init__(self, target: F) -> None:
        ...

    def __call__(self, wrapped: Callable[..., Any]) -> F:
        return cast(F, wrapped)


class _injected_self_func(Generic[T, P, R], Protocol):  # type: ignore
    @overload
    @staticmethod
    def __call__(*args: P.args, **kwargs: P.kwargs) -> R:
        ...

    @overload
    @staticmethod
    def __call__(self: T, *args: P.args, **kwargs: P.kwargs) -> R:
        ...

    @overload
    @staticmethod
    def __call__(cls: type[T], *args: P.args, **kwargs: P.kwargs) -> R:
        ...

    @staticmethod  # type: ignore
    def __call__(*args: Any, **kwds: Any) -> Any:
        ...


self_objects_cache = dict[type[T], T]()


class inject_self(Generic[T, P, R]):
    def __init__(self, function: Callable[Concatenate[T, P], R], /, *, cache: bool = False) -> None:
        self.function = function
        self.cache = cache

    def __get__(
        self, class_obj: T | None, class_type: type[T]
    ) -> _injected_self_func[T, P, R]:
        def _wrapper(*args: Any, **kwargs: Any) -> Any:
            if (
                (is_obj := isinstance(args[0], class_type))
                or isinstance(args[0], type(class_type))
                or args[0] is class_type
            ):
                obj = args[0] if is_obj else args[0]()
                args = args[1:]
            elif class_obj is None:
                if self_objects_cache:
                    if class_type not in self_objects_cache:
                        self_objects_cache[class_type] = class_type()
                    obj = self_objects_cache[class_type]
                else:
                    obj = class_type()
            else:
                obj = class_obj

            return self.function(obj, *args, **kwargs)

        return _wrapper

    @staticmethod
    def cached(function: Callable[Concatenate[T, P], R]) -> inject_self[T, P, R]:
        return inject_self(function, cache=True)
