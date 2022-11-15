from __future__ import annotations

from inspect import isclass
from typing import Any, Callable, Concatenate, Generator, Generic, Iterable, Protocol, Sequence, cast, overload

from .builtins import F0, P0, P1, R0, R1, T0, T1, P, R, T

__all__ = [
    'copy_signature',

    'inject_self',

    'complex_hash',

    'get_subclasses',

    'classproperty'
]


class copy_signature(Generic[F0]):
    def __init__(self, target: F0) -> None:
        ...

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
        def _wrapper(function: Callable[Concatenate[T0, P0], R0]) -> inject_self[T0, P0, R0]:
            inj = cls(function)  # type: ignore
            inj.args = args
            inj.kwargs = kwargs
            return inj  # type: ignore
        return _wrapper


class inject_self(Generic[T, P, R], inject_self_base[T, P, R]):  # type: ignore
    class cached(Generic[T0, P0, R0], inject_self_base[T0, P0, R0]):  # type: ignore
        ...


class complex_hash(Generic[T]):
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


def get_subclasses(family: type[T], exclude: Sequence[type[T]] = []) -> list[type[T]]:
    def _subclasses(cls: type[T]) -> Generator[type[T], None, None]:
        for subclass in cls.__subclasses__():
            yield from _subclasses(subclass)
            if subclass in exclude:
                continue
            yield subclass

    return list(set(_subclasses(family)))


class classproperty(Generic[T, P, R, P0, R0, P1, R1]):
    fget: Callable[[Any], Any] | None
    fset: Callable[[Any, Any], None] | None
    fdel: Callable[[Any], None] | None

    __isabstractmethod__: bool = False

    class metaclass(type):
        def __setattr__(self, key, value):
            if key in self.__dict__:
                obj = self.__dict__.get(key)

            if obj and type(obj) is classproperty:
                return obj.__set__(self, value)

            return super(classproperty.metaclass, self).__setattr__(key, value)

    def __init__(
        self,
        fget: Callable[P, R] | None = None,
        fset: Callable[[T0, T1], None] | None = None,
        fdel: Callable[P0, None] | None = None,
        doc: str | None = None,
    ) -> None:
        if not isinstance(fget, (classmethod, staticmethod)):
            fget = classmethod(fget)

        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        self.doc = doc

    def _wrap(self, func: Callable[P1, R1]) -> Callable[P1, R1]:
        if not isinstance(func, (classmethod, staticmethod)):
            func = classmethod(func)

        return func

    def getter(self, __fget: Callable[P, R]) -> classproperty:
        self.fget = self._wrap(__fget)

        return self

    def setter(self, __fset: Callable[[T0, T1], None]) -> classproperty:
        self.fset = self._wrap(__fset)

        return self

    def deleter(self, __fdel: Callable[P0, None]) -> classproperty:
        self.fdel = self._wrap(__fdel)

        return self

    def __get__(self, __obj: Any, __type: type | None = ...) -> R:
        if __type is None:
            __type = type(__obj)

        return self.fget.__get__(__obj, __type)()

    def __set__(self, __obj: Any, __value: T1) -> None:
        from ..exceptions import CustomError

        if not self.fset:
            raise CustomError[AttributeError]("Can't set attribute")

        if isclass(__obj):
            type_, __obj = __obj, None
        else:
            type_ = type(__obj)

        return self.fset.__get__(__obj, type_)(__value)

    def __delete__(self, __obj: Any) -> None:
        from ..exceptions import CustomError

        if not self.fdel:
            raise CustomError[AttributeError]("Can't delete attribute")

        if isclass(__obj):
            type_, __obj = __obj, None
        else:
            type_ = type(__obj)

        return self.fset.__delete__(__obj, type_)(__obj)
