from __future__ import annotations

from functools import lru_cache
from typing import Any, Callable, Concatenate, Generator, Generic, Iterable, Protocol, Sequence, cast, overload

from .builtins import F0, P0, R0, T0, P, R, T

__all__ = [
    'copy_signature',

    'inject_self',

    'complex_hash',

    'get_subclasses'
]


class copy_signature(Generic[F0]):
    """
    Type util to copy the signature of one function to another function.\n
    Especially useful for passthrough functions.
    ```
    class SomeClass:
        def __init__(
            self, some: Any, complex: Any, /, *args: Any,
            long: Any, signature: Any, **kwargs: Any
        ) -> None:
            ...

    class SomeClassChild(SomeClass):
        @copy_signature(SomeClass.__init__)
        def __init__(*args: Any, **kwargs: Any) -> None:
            super().__init__(*args, **kwargs)
            # do some other thing

    class Example(SomeClass):
        @copy_signature(SomeClass.__init__)
        def __init__(*args: Any, **kwargs: Any) -> None:
            super().__init__(*args, **kwargs)
            # another thing
    ```
    """

    def __init__(self, target: F0) -> None:
        """Copy the signature of ``target``."""

    def __call__(self, wrapped: Callable[..., Any]) -> F0:
        return cast(F0, wrapped)


class injected_self_func(Generic[T, P, R], Protocol):
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
    def __call__(self: T, _self: T, *args: P.args, **kwargs: P.kwargs) -> R:
        ...

    @overload
    @staticmethod
    def __call__(cls: type[T], *args: P.args, **kwargs: P.kwargs) -> R:
        ...

    @overload
    @staticmethod
    def __call__(cls: type[T], _cls: type[T], *args: P.args, **kwargs: P.kwargs) -> R:
        ...

    @staticmethod  # type: ignore
    def __call__(*args: Any, **kwds: Any) -> Any:
        ...


self_objects_cache = dict[type[T], T]()


class inject_self_base(Generic[T, P, R]):
    def __init__(self, function: Callable[Concatenate[T, P], R], /, *, cache: bool = False) -> None:
        """
        Wrap ``function`` to always have a self provided to it.

        :param function:    Method to wrap.
        :param cache:       Whether to cache the self object.
        """

        self.function = function
        if isinstance(self, inject_self.cached):
            self.cache = True
        else:
            self.cache = cache
        self.args = tuple[Any]()
        self.kwargs = dict[str, Any]()

    def __get__(self, class_obj: T | None, class_type: type[T]) -> injected_self_func[T, P, R]:
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

    @classmethod
    def with_args(
        cls, *args: Any, **kwargs: Any
    ) -> Callable[[Callable[Concatenate[T0, P0], R0]], inject_self[T0, P0, R0]]:
        """Provide custom args to instantiate the ``self`` object with."""

        def _wrapper(function: Callable[Concatenate[T0, P0], R0]) -> inject_self[T0, P0, R0]:
            inj = cls(function)  # type: ignore
            inj.args = args
            inj.kwargs = kwargs
            return inj  # type: ignore
        return _wrapper


class inject_self(Generic[T, P, R], inject_self_base[T, P, R]):  # type: ignore
    """Wrap a method so it always has a constructed ``self`` provided to it."""

    class cached(Generic[T0, P0, R0], inject_self_base[T0, P0, R0]):  # type: ignore
        """
        Wrap a method so it always has a constructed ``self`` provided to it.
        Once ``self`` is constructed, it will be reused.
        """


class complex_hash(Generic[T]):
    """
    Decorator for classes to add a ``__hash__`` method to them.

    Especially useful for NamedTuples.
    """

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
        """
        Recursively hash every unhashable object in ``*args``.

        :param *args:   Objects to be hashed.

        :return:        Hash of all the combined objects' hashes.
        """

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


@lru_cache
def get_subclasses(family: type[T], exclude: Sequence[type[T]] = []) -> list[type[T]]:
    """@@PLACEHOLDER@@"""

    def _subclasses(cls: type[T]) -> Generator[type[T], None, None]:
        for subclass in cls.__subclasses__():
            yield from _subclasses(subclass)
            if subclass in exclude:
                continue
            yield subclass

    return list(set(_subclasses(family)))
