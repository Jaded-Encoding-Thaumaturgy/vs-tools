from __future__ import annotations

from enum import Enum
from typing import Any

from ..exceptions import NotFoundEnumValue
from ..types import EnumFuncExceptT, SelfEnum

__all__ = [
    'CustomEnum', 'CustomIntEnum', 'CustomStrEnum'
]


class CustomEnum(Enum):
    @classmethod
    def from_param(cls: type[SelfEnum], value: Any, func_except: EnumFuncExceptT | None = None) -> SelfEnum | None:
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

            raise NotFoundEnumValue(f'{func_name}{var_name} must be in {readable_enum}.', func_except) from None


class CustomIntEnum(int, CustomEnum):
    ...


class CustomStrEnum(str, CustomEnum):
    ...
