from __future__ import annotations

from typing import TYPE_CHECKING, Any, overload

import vapoursynth as vs

from ..types import FuncExceptT
from .base import CustomIntEnum

if TYPE_CHECKING:
    from .color import ColorRange, ColorRangeT, Matrix, MatrixT, Primaries, PrimariesT, Transfer, TransferT
    from .generic import ChromaLocation, ChromaLocationT, FieldBased, FieldBasedT

    class _MatrixMeta(CustomIntEnum, vs.MatrixCoefficients):  # type: ignore
        def __new__(cls: type[Matrix], value: MatrixT) -> Matrix:  # type: ignore
            ...

        @overload
        @classmethod
        def from_param(  # type: ignore
            cls: type[Matrix], value: None, func_except: FuncExceptT | None = None
        ) -> None:
            ...

        @overload
        @classmethod
        def from_param(  # type: ignore
            cls: type[Matrix], value: int | Matrix | MatrixT, func_except: FuncExceptT | None = None
        ) -> Matrix:
            ...

        @overload
        @classmethod
        def from_param(  # type: ignore
            cls: type[Matrix], value: int | Matrix | MatrixT | None, func_except: FuncExceptT | None = None
        ) -> Matrix | None:
            ...

        @classmethod
        def from_param(cls: Any, value: Any, func_except: Any = None) -> Matrix | None:
            """
            Determine the Matrix through a parameter.

            :param value:           Value or Matrix object.
            :param func_except:     Exception function.

            :return:                Matrix object or None.
            """

    class _TransferMeta(CustomIntEnum, vs.TransferCharacteristics):  # type: ignore
        def __new__(cls: type[Transfer], value: TransferT) -> Transfer:  # type: ignore
            ...

        @overload
        @classmethod
        def from_param(  # type: ignore
            cls: type[Transfer], value: None, func_except: FuncExceptT | None = None
        ) -> None:
            ...

        @overload
        @classmethod
        def from_param(  # type: ignore
            cls: type[Transfer], value: int | Transfer | TransferT, func_except: FuncExceptT | None = None
        ) -> Transfer:
            ...

        @overload
        @classmethod
        def from_param(  # type: ignore
            cls: type[Transfer], value: int | Transfer | TransferT | None, func_except: FuncExceptT | None = None
        ) -> Transfer | None:
            ...

        @classmethod
        def from_param(cls: Any, value: Any, func_except: Any = None) -> Transfer | None:
            """
            Determine the Transfer through a parameter.

            :param value:           Value or Transfer object.
            :param func_except:     Exception function.

            :return:                Transfer object or None.
            """

    class _PrimariesMeta(CustomIntEnum, vs.ColorPrimaries):  # type: ignore
        def __new__(cls: type[Primaries], value: PrimariesT) -> Primaries:  # type: ignore
            ...

        @overload
        @classmethod
        def from_param(  # type: ignore
            cls: type[Primaries], value: None, func_except: FuncExceptT | None = None
        ) -> None:
            ...

        @overload
        @classmethod
        def from_param(  # type: ignore
            cls: type[Primaries], value: int | Primaries | PrimariesT, func_except: FuncExceptT | None = None
        ) -> Primaries:
            ...

        @overload
        @classmethod
        def from_param(  # type: ignore
            cls: type[Primaries], value: int | Primaries | PrimariesT | None, func_except: FuncExceptT | None = None
        ) -> Primaries | None:
            ...

        @classmethod
        def from_param(cls: Any, value: Any, func_except: Any = None) -> Primaries | None:
            """
            Determine the Primaries through a parameter.

            :param value:           Value or Primaries object.
            :param func_except:     Exception function.

            :return:                Primaries object or None.
            """

    class _ColorRangeMeta(CustomIntEnum, vs.ColorPrimaries):  # type: ignore
        def __new__(cls: type[ColorRange], value: ColorRangeT) -> ColorRange:  # type: ignore
            ...

        @overload
        @classmethod
        def from_param(  # type: ignore
            cls: type[ColorRange], value: None, func_except: FuncExceptT | None = None
        ) -> None:
            ...

        @overload
        @classmethod
        def from_param(  # type: ignore
            cls: type[ColorRange], value: int | ColorRange | ColorRangeT, func_except: FuncExceptT | None = None
        ) -> ColorRange:
            ...

        @overload
        @classmethod
        def from_param(  # type: ignore
            cls: type[ColorRange], value: int | ColorRange | ColorRangeT | None, func_except: FuncExceptT | None = None
        ) -> ColorRange | None:
            ...

        @classmethod
        def from_param(cls: Any, value: Any, func_except: Any = None) -> ColorRange | None:
            """
            Determine the ColorRange through a parameter.

            :param value:           Value or ColorRange object.
            :param func_except:     Exception function.

            :return:                ColorRange object or None.
            """

    class _ChromaLocationMeta(CustomIntEnum, vs.ChromaLocation):  # type: ignore
        def __new__(cls: type[ChromaLocation], value: ChromaLocationT) -> ChromaLocation:  # type: ignore
            ...

        @overload
        @classmethod
        def from_param(  # type: ignore
            cls: type[ChromaLocation], value: None, func_except: FuncExceptT | None = None
        ) -> None:
            ...

        @overload
        @classmethod
        def from_param(  # type: ignore
            cls: type[ChromaLocation], value: int | ChromaLocation | ChromaLocationT,
            func_except: FuncExceptT | None = None
        ) -> ChromaLocation:
            ...

        @overload
        @classmethod
        def from_param(  # type: ignore
            cls: type[ChromaLocation], value: int | ChromaLocation | ChromaLocationT | None,
            func_except: FuncExceptT | None = None
        ) -> ChromaLocation | None:
            ...

        @classmethod
        def from_param(cls: Any, value: Any, func_except: Any = None) -> ChromaLocation | None:
            """
            Determine the ChromaLocation through a parameter.

            :param value:           Value or ChromaLocation object.
            :param func_except:     Exception function.

            :return:                ChromaLocation object or None.
            """

    class _FieldBasedMeta(CustomIntEnum, vs.FieldBased):  # type: ignore
        def __new__(cls: type[FieldBased], value: FieldBasedT) -> FieldBased:  # type: ignore
            ...

        @overload
        @classmethod
        def from_param(  # type: ignore
            cls: type[FieldBased], value_or_tff: None, func_except: FuncExceptT | None = None
        ) -> None:
            ...

        @overload
        @classmethod
        def from_param(  # type: ignore
            cls: type[FieldBased], value_or_tff: int | FieldBasedT | bool, func_except: FuncExceptT | None = None
        ) -> FieldBased:
            ...

        @overload
        @classmethod
        def from_param(  # type: ignore
            cls: type[FieldBased], value_or_tff: int | FieldBasedT | bool | None, func_except: FuncExceptT | None = None
        ) -> FieldBased | None:
            ...

        @classmethod
        def from_param(cls: Any, value_or_tff: Any, func_except: Any = None) -> FieldBased | None:
            """
            Determine the ChromaLocation through a parameter.

            :param value_or_tff:    Value or FieldBased object.
                                    If it's bool, it specifies for wheter it's tff of bff.
            :param func_except:     Exception function.

            :return:                FieldBased object or None.
            """
else:
    _MatrixMeta = _TransferMeta = _PrimariesMeta = _ColorRangeMeta = CustomIntEnum
    _ChromaLocationMeta = _FieldBasedMeta = CustomIntEnum
