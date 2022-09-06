from __future__ import annotations

from enum import Enum
from typing import Any, Callable, TypeVar

from ..exceptions import NotFoundEnumValue

__all__ = [
    'FuncExceptT',
    'CustomEnum', 'CustomIntEnum', 'CustomStrEnum'
]

FuncExceptT = str | tuple[Callable[..., Any] | str, str]  # type: ignore


class CustomEnum(Enum):
    @classmethod
    def from_param(cls: type[SelfEnum], value: Any, func_except: FuncExceptT | None = None) -> SelfEnum | None:
        if value is None:
            return None

        if func_except is None:
            return cls(value)

        try:
            return cls(value)
        except ValueError:
            readable_enum = ', '.join([repr(i) for i in cls])

            if not isinstance(func_except, str):
                from ..functions import norm_func_name

                func_name, var_name = func_except

                func_name = norm_func_name(func_name)
            else:
                var_name, func_name = func_except, ''

            raise NotFoundEnumValue(f'{func_name}{var_name} must be in {readable_enum}.') from None


SelfEnum = TypeVar('SelfEnum', bound=Enum)


class CustomIntEnum(int, CustomEnum):
    ...


class CustomStrEnum(str, CustomEnum):
    ...
