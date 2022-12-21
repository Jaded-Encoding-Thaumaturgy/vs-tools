from __future__ import annotations

from abc import ABC, ABCMeta
from functools import partial
from inspect import Signature, isclass
from typing import (
    TYPE_CHECKING, Any, Callable, Concatenate, Generator, Generic, Iterable, Protocol, Sequence, TypeVar, cast, overload
)

from .builtins import F, F0, P0, P1, R0, R1, T0, T1, T2, KwargsT, P, R, T

__all__ = [
    'copy_signature',

    'inject_self',

    'complex_hash',

    'get_subclasses',

    'classproperty', 'cachedproperty',

    'KwargsNotNone',

    'vs_object', 'VSDebug',

    'Singleton'
]


class copy_signature(Generic[F0]):
    def __init__(self, target: F0) -> None:
        ...

    def __call__(self, wrapped: Callable[..., Any]) -> F0:
        return cast(F0, wrapped)


class injected_self_func(Generic[T, P, R], Protocol):  # type: ignore[misc]
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
        signature = Signature.from_callable(self.function, follow_wrapped=True, eval_str=True)
        first_key = next(iter(list(signature.parameters.keys())), None)

        def _wrapper(*args: Any, **kwargs: Any) -> Any:
            first_arg = (args[0] if args else None) or (kwargs.get(first_key, None) if first_key else None)

            if (
                first_arg and (
                    (is_obj := isinstance(first_arg, class_type))
                    or isinstance(first_arg, type(class_type))
                    or first_arg is class_type
                )
            ):
                obj = first_arg if is_obj else first_arg()
                if args:
                    args = args[1:]
                elif kwargs and first_key:
                    kwargs.pop(first_key)
            elif class_obj is None:
                if self.cache:
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


class classproperty(Generic[P, R, T, T0, P0]):
    __isabstractmethod__: bool = False

    class metaclass(type):
        def __setattr__(self, key: str, value: Any) -> None:
            if key in self.__dict__:
                obj = self.__dict__.get(key)

            if obj and type(obj) is classproperty:
                return obj.__set__(self, value)

            return super(classproperty.metaclass, self).__setattr__(key, value)

    def __init__(
        self,
        fget: classmethod[R] | Callable[P, R],
        fset: classmethod[None] | Callable[[T, T0], None] | None = None,
        fdel: classmethod[None] | Callable[P0, None] | None = None,
        doc: str | None = None,
    ) -> None:
        if not isinstance(fget, (classmethod, staticmethod)):
            fget = classmethod(fget)

        self.fget = self._wrap(fget)
        self.fset = self._wrap(fset) if fset is not None else fset
        self.fdel = self._wrap(fdel) if fdel is not None else fdel

        self.doc = doc

    def _wrap(self, func: classmethod[R1] | Callable[P1, R1]) -> classmethod[R1]:
        if not isinstance(func, (classmethod, staticmethod)):
            func = classmethod(func)

        return func

    def getter(self, __fget: classmethod[R] | Callable[P1, R1]) -> classproperty[P1, R1, T, T0, P0]:
        self.fget = self._wrap(__fget)  # type: ignore
        return self  # type: ignore

    def setter(self, __fset: classmethod[None] | Callable[[T1, T2], None]) -> classproperty[P, R, T1, T2, P0]:
        self.fset = self._wrap(__fset)
        return self  # type: ignore

    def deleter(self, __fdel: classmethod[None] | Callable[P1, None]) -> classproperty[P, R, T, T0, P1]:
        self.fdel = self._wrap(__fdel)
        return self  # type: ignore

    def __get__(self, __obj: Any, __type: type | None = None) -> R:
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

        return self.fdel.__delete__(__obj, type_)(__obj)  # type: ignore


class cachedproperty(property, Generic[P, R, T, T0, P0]):
    __isabstractmethod__: bool = False

    cache_key = '_vst_cachedproperty_cache'

    class baseclass(object):
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, **kwargs)
            self.__dict__.__setitem__(cachedproperty.cache_key, dict[str, Any]())

    if TYPE_CHECKING:
        def __init__(
            self, fget: Callable[P, R], fset: Callable[[T, T0], None] | None = None,
            fdel: Callable[P0, None] | None = None, doc: str | None = None,
        ) -> None:
            ...

        def getter(self, __fget: Callable[P1, R1]) -> cachedproperty[P1, R1, T, T0, P0]:
            ...

        def setter(self, __fset: Callable[[T1, T2], None]) -> cachedproperty[P, R, T1, T2, P0]:
            ...

        def deleter(self, __fdel: Callable[P1, None]) -> cachedproperty[P, R, T, T0, P1]:
            ...

    def __get__(self, __obj: Any, __type: type | None = None) -> R:
        function = self.fget.__get__(__obj, __type)  # type: ignore

        cache = __obj.__dict__.get(cachedproperty.cache_key)
        name = function.__name__

        if name not in cache:
            cache[name] = function()

        return cache[name]  # type: ignore


class KwargsNotNone(KwargsT):
    if not TYPE_CHECKING:
        def __new__(cls, *args: Any, **kwargs: Any) -> KwargsNotNone:
            return KwargsT(**{
                key: value for key, value in KwargsT(*args, **kwargs).items()
                if value is not None
            })


class vs_object(ABC, metaclass=ABCMeta):
    __vsdel_register: Callable[[int], None] | None = None

    def __new__(cls: type[VSObjSelf], *args: Any, **kwargs: Any) -> VSObjSelf:
        from ..utils.vs_proxy import register_on_creation, register_on_destroy

        try:
            self = super().__new__(cls, *args, **kwargs)
        except TypeError:
            self = super().__new__(cls)

        if hasattr(self, '__vs_del__'):
            def _register(core_id: int) -> None:
                register_on_destroy(partial(self.__vs_del__, core_id))

            # [un]register_on_creation/destroy will only hold a weakref to the object
            self.__vsdel_register = _register
            register_on_creation(self.__vsdel_register)

        return self

    def __post_init__(self) -> None:
        ...

    if TYPE_CHECKING:
        def __vs_del__(self, core_id: int) -> None:
            ...

    @staticmethod
    def core_unbound(deleter: F) -> F:
        deleter._is_core_unbound = True  # type: ignore
        return deleter


VSObjSelf = TypeVar('VSObjSelf', bound=vs_object)

SingleMeta = TypeVar('SingleMeta', bound=type)


class SingletonMeta(type):
    _instances = dict[type[SingleMeta], SingleMeta]()
    _singleton_init: bool

    def __new__(
        cls: type[SingletonSelf], name: str, bases: tuple[type, ...], namespace: dict[str, Any], **kwargs: Any
    ) -> SingletonSelf:
        return type.__new__(cls, name, bases, namespace | {'_singleton_init': kwargs.pop('init', False)})

    def __call__(cls: type[SingletonSelf], *args: Any, **kwargs: Any) -> SingletonSelf:  # type: ignore
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        elif cls._singleton_init:
            cls._instances[cls].__init__(*args, **kwargs)  # type: ignore

        return cls._instances[cls]


SingletonSelf = TypeVar('SingletonSelf', bound=SingletonMeta)


class Singleton(metaclass=SingletonMeta):
    ...


class VSDebug(Singleton, init=True):
    def __init__(self, *, env_life: bool = True, core_fetch: bool = False) -> None:
        from ..utils.vs_proxy import register_on_creation

        if env_life:
            register_on_creation(VSDebug._print_env_live)

        if core_fetch:
            register_on_creation(VSDebug._print_stack)

    @staticmethod
    def _print_stack(core_id: int) -> None:
        raise Exception

    @staticmethod
    def _print_env_live(core_id: int) -> None:
        from ..utils.vs_proxy import register_on_destroy, core, get_current_environment

        print(f'New core created with id: {core_id}')

        core.register_on_destroy(VSDebug._print_core_destroy)
        register_on_destroy(partial(VSDebug._print_destroy, get_current_environment().env_id, core_id))

    @staticmethod
    def _print_destroy(env_id: int, core_id: int) -> None:
        print(f'Environment destroyed with id: {env_id}, current core id: {core_id}')

    @staticmethod
    def _print_core_destroy(_: int, core_id: int) -> None:
        print(f'Core destroyed with id: {core_id}')
