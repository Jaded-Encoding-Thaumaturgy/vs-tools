from __future__ import annotations

from enum import Enum
from typing import Any, TypeVar

from ..exceptions import CustomValueError, NotFoundEnumValue
from ..types import FuncExceptT

__all__ = [
    'SelfEnum',
    'CustomEnum', 'CustomIntEnum', 'CustomStrEnum'
]


class CustomEnum(Enum):
    """Base class for custom enums."""

    @classmethod
    def _missing_(cls: type[SelfEnum], value: Any) -> SelfEnum | None:
        return cls.from_param(value)

    @classmethod
    def from_param(cls: type[SelfEnum], value: Any, func_except: FuncExceptT | None = None) -> SelfEnum | None:
        """
        Return the enum value from a parameter.

        :param value:               Value to instantiate the enum class.
        :param func_except:         Exception function.

        :return:                    Enum value.

        :raises NotFoundEnumValue:   Variable not found in the given enum.
        """

        if value is None:
            return None

        if func_except is None:
            func_except = cls.from_param

        if isinstance(value, cls):
            return value

        if value is cls:
            raise CustomValueError('You must select a member, not pass the enum!', func_except)

        try:
            return cls(value)
        except ValueError:
            ...

        if isinstance(func_except, tuple):
            func_name, var_name = func_except
        else:
            func_name, var_name = func_except, ''

        raise NotFoundEnumValue(
            'Value for "{var_name}" argument must be a valid {enum_name}.\n'
            'It can be a value in [{readable_enum}].', func_name,
            var_name=var_name, enum_name=cls,
            readable_enum=iter([f'{x.name} ({x.value})' for x in cls])
        )


class CustomIntEnum(int, CustomEnum):
    """Base class for custom int enums."""

    value: int


class CustomStrEnum(str, CustomEnum):
    """Base class for custom str enums."""

    value: str


SelfEnum = TypeVar('SelfEnum', bound=CustomEnum)
