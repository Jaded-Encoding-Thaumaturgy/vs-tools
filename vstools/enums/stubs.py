from __future__ import annotations

from string import capwords
from typing import TYPE_CHECKING, Any, Iterable, TypeVar, overload

import vapoursynth as vs

from ..types import MISSING, FuncExceptT, classproperty
from .base import CustomIntEnum
from ..exceptions import CustomError

__all__ = [
    'PropEnum',

    '_base_from_video',

    '_MatrixMeta',
    '_TransferMeta',
    '_PrimariesMeta',
    '_ColorRangeMeta',
    '_ChromaLocationMeta',
    '_FieldBasedMeta'
]


class PropEnum(CustomIntEnum):
    @classmethod
    def is_unknown(cls: type[SelfPropEnum], value: int | SelfPropEnum) -> bool:
        return False

    @classproperty
    def prop_key(cls: type[SelfPropEnum]) -> str:  # type: ignore
        return f'_{cls.__name__}'

    if TYPE_CHECKING:
        def __new__(
            cls: type[SelfPropEnum], value: int | SelfPropEnum | vs.VideoNode | vs.VideoFrame | vs.FrameProps
        ) -> SelfPropEnum:
            ...

        @overload
        @classmethod
        def from_param(
            cls: type[SelfPropEnum], value: None, func_except: FuncExceptT | None = None
        ) -> None:
            ...

        @overload
        @classmethod
        def from_param(
            cls: type[SelfPropEnum], value: int | SelfPropEnum, func_except: FuncExceptT | None = None
        ) -> SelfPropEnum:
            ...

        @overload
        @classmethod
        def from_param(
            cls: type[SelfPropEnum], value: int | SelfPropEnum | None, func_except: FuncExceptT | None = None
        ) -> SelfPropEnum | None:
            ...

        @classmethod
        def from_param(cls: Any, value: Any, func_except: Any = None) -> SelfPropEnum | None:
            ...

    @classmethod
    def _missing_(cls: type[SelfPropEnum], value: Any) -> SelfPropEnum | None:
        if isinstance(value, vs.VideoNode | vs.VideoFrame | vs.FrameProps):
            return cls.from_video(value, True)
        return super().from_param(value)

    @classmethod
    def from_res(cls: type[SelfPropEnum], frame: vs.VideoNode | vs.VideoFrame) -> SelfPropEnum:
        raise NotImplementedError

    @classmethod
    def from_video(
        cls: type[SelfPropEnum], src: vs.VideoNode | vs.VideoFrame | vs.FrameProps, strict: bool = False,
        func: FuncExceptT | None = None
    ) -> SelfPropEnum:
        raise NotImplementedError

    @classmethod
    def ensure_presence(
        cls: type[SelfPropEnum], clip: vs.VideoNode, value: int | SelfPropEnum | None, func: FuncExceptT | None = None
    ) -> vs.VideoNode:
        enum_value = cls.from_param(value, func) or cls.from_video(clip, True)

        return clip.std.SetFrameProp(enum_value.prop_key, enum_value.value)

    @staticmethod
    def ensure_presences(
        clip: vs.VideoNode, prop_enums: Iterable[type[SelfPropEnum] | SelfPropEnum], func: FuncExceptT | None = None
    ) -> vs.VideoNode:
        return clip.std.SetFrameProps(**{
            value.prop_key: value.value  # type: ignore
            for value in [
                cls if isinstance(cls, PropEnum) else cls.from_video(clip, True)
                for cls in prop_enums
            ]
        })

    @property
    def pretty_string(self) -> str:
        return capwords(self.string.replace('_', ' '))

    @property
    def string(self) -> str:
        return self._name_.lower()

    @classmethod
    def is_valid(cls, value: int) -> bool:
        return value in map(int, cls.__members__.values())


SelfPropEnum = TypeVar('SelfPropEnum', bound=PropEnum)


def _base_from_video(
    cls: type[SelfPropEnum], src: vs.VideoNode | vs.VideoFrame | vs.FrameProps, exception: type[CustomError],
    strict: bool, func: FuncExceptT | None = None
) -> SelfPropEnum:
    from ..utils import get_prop
    from ..functions import fallback

    func = fallback(func, cls.from_video)  # type: ignore

    value = get_prop(src, cls, int, default=MISSING if strict else None)

    if value is None or cls.is_unknown(value):  # type: ignore
        if strict:
            raise exception('{class_name} is undefined.', func, class_name=cls, reason=value)

        if isinstance(src, vs.FrameProps):
            raise exception('Can\'t determine {class_name} from FrameProps.', func, class_name=cls)

        return cls.from_res(src)  # type: ignore

    return cls(value)  # type: ignore


if TYPE_CHECKING:
    from .color import ColorRange, ColorRangeT, Matrix, MatrixT, Primaries, PrimariesT, Transfer, TransferT
    from .generic import ChromaLocation, ChromaLocationT, FieldBased, FieldBasedT

    class _MatrixMeta(PropEnum, vs.MatrixCoefficients):  # type: ignore
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
            ...

    class _TransferMeta(PropEnum, vs.TransferCharacteristics):  # type: ignore
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
            ...

    class _PrimariesMeta(PropEnum, vs.ColorPrimaries):  # type: ignore
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
            ...

    class _ColorRangeMeta(PropEnum, vs.ColorPrimaries):  # type: ignore
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
            ...

    class _ChromaLocationMeta(PropEnum, vs.ChromaLocation):  # type: ignore
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
            ...

    class _FieldBasedMeta(PropEnum, vs.FieldBased):  # type: ignore
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

        @classmethod  # type: ignore
        def from_param(cls: Any, value: Any, func_except: Any = None) -> FieldBased | None:
            ...

        @classmethod
        def ensure_presence(
            cls, clip: vs.VideoNode, tff: bool | int | FieldBasedT | None, func: FuncExceptT | None = None
        ) -> vs.VideoNode:
            ...
else:
    _MatrixMeta = _TransferMeta = _PrimariesMeta = _ColorRangeMeta = PropEnum
    _ChromaLocationMeta = PropEnum

    class _FieldBasedMeta(PropEnum):
        @classmethod
        def ensure_presence(
            cls, clip: vs.VideoNode, tff: bool | int | FieldBased | None, func: FuncExceptT | None = None
        ) -> vs.VideoNode:
            value = cls.from_param(tff, func) or cls.from_video(clip, True)

            return clip.std.SetFieldBased(value.value)
