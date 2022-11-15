from __future__ import annotations

from enum import Enum
from typing import Any

from ..exceptions import NotFoundEnumValue, CustomValueError
from ..types import EnumFuncExceptT, SelfEnum

__all__ = [
    'CustomEnum', 'CustomIntEnum', 'CustomStrEnum'
]


class CustomEnum(Enum):
    @classmethod
    def _missing_(cls: type[SelfEnum], value: Any) -> SelfEnum:
        return cls.from_param(value)

    @classmethod
    def from_param(cls: type[SelfEnum], value: Any, func_except: EnumFuncExceptT | None = None) -> SelfEnum | None:
        if value is None:
            return None

        if func_except is None:
            func_except = cls.from_param

        if isinstance(value, cls):
            return value

        if value is cls:
            raise CustomValueError('You must select a memeber, not pass the enum!', func_except)

        try:
            return cls(value)
        except ValueError:
            ...

        if not isinstance(func_except, str):
            func_name, var_name = func_except
        else:
            var_name, func_name = func_except, ''

        raise NotFoundEnumValue(
            'Value for "{var_name}" argument must be a valid {enum_name}.\n'
            'It can be a value in [{readable_enum}].', func_name,
            var_name=var_name, enum_name=cls,
            readable_enum=iter([f'{x.name} ({x.value})' for x in cls])
        )


class CustomIntEnum(int, CustomEnum):
    ...


class CustomStrEnum(str, CustomEnum):
    ...
