from __future__ import annotations

from typing import Any, Callable, Concatenate, Generic, Iterable, Protocol, cast, overload

from .builtins import P0, R0, T0, F, P, R, T

__all__ = [
    'copy_signature',

    'inject_self',

    'complex_hash'
]


class copy_signature(Generic[F]):
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
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
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    def __init__(self, function: Callable[Concatenate[T, P], R], /, *, cache: bool = False) -> None:
        """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
        self.function = function
        if isinstance(self, cached_inject_self):
            self.cache = True
        else:
            self.cache = cache
        self.args = tuple[Any]()
        self.kwargs = dict[str, Any]()

    def __get__(self, class_obj: T | None, class_type: type[T]) -> _injected_self_func[T, P, R]:
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
                        obj = self_objects_cache[class_type] = class_type(*self.args, **self.kwargs)
                    else:
                        obj = self_objects_cache[class_type]
                else:
                    obj = class_type(*self.args, **self.kwargs)
            else:
                obj = class_obj

            return self.function(obj, *args, **kwargs)

        return _wrapper

    # TODO fix cached typing

    @classmethod
    def with_args(
        cls, *args: Any, **kwargs: Any
    ) -> Callable[[Callable[Concatenate[T0, P0], R0]], inject_self[T0, P0, R0]]:
        """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
        def _wrapper(function: Callable[Concatenate[T0, P0], R0]) -> inject_self[T0, P0, R0]:
            inj = cls(function)  # type: ignore
            inj.args = args
            inj.kwargs = kwargs
            return inj  # type: ignore
        return _wrapper


class cached_inject_self(Generic[T, P, R], inject_self[T, P, R]):  # type: ignore
    cache = True


inject_self.cached = cached_inject_self  # type: ignore


class complex_hash(Generic[T]):
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    def __new__(cls, class_type: T) -> T:  # type: ignore
        class inner_class_type(class_type):  # type: ignore
            def __hash__(self) -> int:
                return complex_hash.hash(
                    self.__class__.__name__, *(
                        getattr(self, key) for key in self.__annotations__.keys()
                    )
                )

        return inner_class_type  # type: ignore

    @staticmethod
    def hash(*args: Any) -> int:
        """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
        values = list[str]()
        for value in args:
            try:
                new_hash = hash(value)
            except TypeError:
                if isinstance(value, Iterable):
                    new_hash = complex_hash.hash(*value)
                else:
                    new_hash = hash(str(value))

            values.append(str(new_hash))

        return hash('_'.join(values))
