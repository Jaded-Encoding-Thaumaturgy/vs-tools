from __future__ import annotations

from typing import Any, NamedTuple, TypeAlias, Union

import vapoursynth as vs

from ..exceptions import (
    ReservedMatrixError, ReservedPrimariesError, ReservedTransferError, UndefinedMatrixError, UndefinedPrimariesError,
    UndefinedTransferError, UnsupportedMatrixError, UnsupportedPrimariesError, UnsupportedTransferError
)
from ..types import MISSING, FuncExceptT, classproperty
from .stubs import PropEnum, _base_from_video, _ColorRangeMeta, _MatrixMeta, _PrimariesMeta, _TransferMeta

__all__ = [
    'PropEnum',

    'Matrix', 'Transfer', 'Primaries',
    'MatrixT', 'TransferT', 'PrimariesT',

    'ColorRange',
    'ColorRangeT',

    'MatrixCoefficients'
]


class Matrix(_MatrixMeta):
    """Matrix coefficients (ITU-T H.265 Table E.5)."""

    _value_: int

    @classmethod
    def _missing_(cls: type[Matrix], value: Any) -> Matrix | None:
        value = super()._missing_(value)

        if value is None:
            return Matrix.UNKNOWN
        elif isinstance(value, cls):
            return value

        if value == 8:
            raise UnsupportedMatrixError(
                'Matrix YCGCO is no longer supported by VapourSynth starting in R55 (APIv4).', 'Matrix'
            )

        if Matrix.RGB < value < Matrix.ICTCP:
            raise ReservedMatrixError(f'Matrix({value}) is reserved.', cls)

        if value > Matrix.ICTCP:
            raise UnsupportedMatrixError(
                f'Matrix({value}) is current unsupported. '
                'If you believe this to be in error, please leave an issue '
                'in the vs-tools GitHub repository.', cls
            )

        return None

    RGB = 0
    GBR = RGB
    BT709 = 1
    UNKNOWN = 2
    FCC = 4
    BT470BG = 5
    BT601 = BT470BG
    SMPTE170M = 6
    SMPTE240M = 7
    BT2020NC = 9
    BT2020C = 10
    SMPTE2085 = 11
    CHROMA_DERIVED_NC = 12
    CHROMA_DERIVED_C = 13
    ICTCP = 14

    @classmethod
    def is_unknown(cls, value: int | Matrix) -> bool:
        return value == cls.UNKNOWN

    @classmethod
    def from_res(cls, frame: vs.VideoNode | vs.VideoFrame) -> Matrix:
        from ..utils import get_var_infos

        fmt, width, height = get_var_infos(frame)

        if fmt.color_family == vs.RGB:
            return Matrix.RGB

        if width <= 1024 and height <= 576:
            if height == 576:
                return Matrix.BT470BG

            return Matrix.SMPTE170M

        if width <= 2048 and height <= 1536:
            return Matrix.BT709

        return Matrix.BT2020NC

    @classmethod
    def from_video(
        cls, src: vs.VideoNode | vs.VideoFrame | vs.FrameProps, strict: bool = False, func: FuncExceptT | None = None
    ) -> Matrix:
        return _base_from_video(cls, src, UndefinedMatrixError, strict, func)

    @classmethod
    def from_transfer(cls, transfer: Transfer, strict: bool = False) -> Matrix:
        if transfer not in _transfer_matrix_map:
            if strict:
                raise UnsupportedTransferError(f'{transfer} is not supported!', cls.from_transfer)

            return cls(transfer.value)

        return _transfer_matrix_map[transfer]

    @classmethod
    def from_primaries(cls, primaries: Primaries, strict: bool = False) -> Matrix:
        if primaries not in _primaries_matrix_map:
            if strict:
                raise UnsupportedPrimariesError(f'{primaries} is not supported!', cls.from_primaries)

            return cls(primaries.value)

        return _primaries_matrix_map[primaries]

    @property
    def pretty_string(self) -> str:
        return _matrix_pretty_name_map.get(self, super().pretty_string)

    @property
    def string(self) -> str:
        return _matrix_name_map.get(self, super().string)


class Transfer(_TransferMeta):
    """Transfer characteristics (ITU-T H.265)."""

    _value_: int

    @classmethod
    def _missing_(cls: type[Transfer], value: Any) -> Transfer | None:
        value = super()._missing_(value)

        if value is None:
            return Transfer.UNKNOWN
        elif isinstance(value, cls):
            return value

        if Transfer.BT709 < value < Transfer.ARIB_B67 or value == 0:
            raise ReservedTransferError(f'Transfer({value}) is reserved.', cls)

        if value > Transfer.ARIB_B67:
            raise UnsupportedTransferError(
                f'Transfer({value}) is current unsupported. '
                'If you believe this to be in error, please leave an issue '
                'in the vs-tools GitHub repository.', cls
            )

        return None

    BT709 = 1
    UNKNOWN = 2
    BT470M = 4
    BT470BG = 5
    BT601 = 6
    ST240M = 7
    LINEAR = 8
    LOG_100 = 9
    LOG_316 = 10
    XVYCC = 11
    SRGB = 13
    BT2020_10bits = 14
    BT2020_12bits = 15
    ST2084 = 16
    ARIB_B67 = 18

    """
    Extra tranfer characterists from libplacebo
    https://github.com/haasn/libplacebo/blob/master/src/include/libplacebo/colorspace.h#L193
    """

    # Standard gamut:
    BT601_525 = 100
    BT601_625 = 101
    EBU_3213 = 102
    # Wide gamut:
    APPLE = 103
    ADOBE = 104
    PRO_PHOTO = 105
    CIE_1931 = 106
    DCI_P3 = 107
    DISPLAY_P3 = 108
    V_GAMUT = 109
    S_GAMUT = 110
    FILM_C = 111

    @classmethod
    def is_unknown(cls, value: int | Transfer) -> bool:
        return value == cls.UNKNOWN

    @classmethod
    def from_res(cls, frame: vs.VideoNode | vs.VideoFrame) -> Transfer:
        from ..utils import get_var_infos

        fmt, width, height = get_var_infos(frame)

        if fmt.color_family == vs.RGB:
            return Transfer.SRGB

        if width <= 1024 and height <= 576:
            if height == 576:
                return Transfer.BT470BG

            return Transfer.BT601

        if width <= 2048 and height <= 1536:
            return Transfer.BT709

        return Transfer.ST2084

    @classmethod
    def from_video(
        cls, src: vs.VideoNode | vs.VideoFrame | vs.FrameProps, strict: bool = False, func: FuncExceptT | None = None
    ) -> Transfer:
        return _base_from_video(cls, src, UndefinedTransferError, strict, func)

    @classmethod
    def from_matrix(cls, matrix: Matrix, strict: bool = False) -> Transfer:
        if matrix not in _matrix_transfer_map:
            if strict:
                raise UnsupportedMatrixError(f'{matrix} is not supported!', cls.from_matrix)

            return cls(matrix.value)

        return _matrix_transfer_map[matrix]

    @classmethod
    def from_primaries(cls, primaries: Primaries, strict: bool = False) -> Transfer:
        if primaries not in _primaries_transfer_map:
            if strict:
                raise UnsupportedPrimariesError(f'{primaries} is not supported!', cls.from_primaries)

            return cls(primaries.value)

        return _primaries_transfer_map[primaries]

    @classmethod
    def from_libplacebo(self, val: int) -> int:
        return _placebo_transfer_map[val]

    @property
    def value_vs(self) -> int:
        if self >= self.BT601_525:
            raise ReservedTransferError(
                'This transfer isn\'t a VapourSynth internal transfer, but a libplacebo one!',
                f'{self.__class__.__name__}.value_vs'
            )

        return self.value

    @property
    def value_libplacebo(self) -> int:
        return _transfer_placebo_map[self]

    @property
    def pretty_string(self) -> str:
        return _transfer_pretty_name_map.get(self, super().pretty_string)
    
    @property
    def string(self) -> str:
        return _transfer_name_map.get(self, super().string)


class Primaries(_PrimariesMeta):
    """Color primaries (ITU-T H.265)."""

    _value_: int

    @classmethod
    def _missing_(cls: type[Primaries], value: Any) -> Primaries | None:
        value = super()._missing_(value)

        if value is None:
            return Primaries.UNKNOWN
        elif isinstance(value, cls):
            return value

        if cls.BT709 < value < cls.EBU3213E:
            raise ReservedPrimariesError(f'Primaries({value}) is reserved.', cls)

        if value > cls.EBU3213E:
            raise UnsupportedPrimariesError(
                f'Primaries({value}) is current unsupported. '
                'If you believe this to be in error, please leave an issue '
                'in the vs-tools GitHub repository.', cls
            )

        return None

    BT709 = 1
    UNKNOWN = 2
    BT470M = 4
    BT470BG = 5
    ST170M = 6
    ST240M = 7
    FILM = 8
    BT2020 = 9
    ST428 = 10
    XYZ = ST428
    ST431_2 = 11
    ST432_1 = 12
    EBU3213E = 22

    @classmethod
    def is_unknown(cls, value: int | Primaries) -> bool:
        return value == cls.UNKNOWN

    @classmethod
    def from_res(cls, frame: vs.VideoNode | vs.VideoFrame) -> Primaries:
        from ..utils import get_var_infos

        fmt, w, h = get_var_infos(frame)

        if fmt.color_family == vs.RGB:
            return Primaries.BT709

        if w <= 1024 and h <= 576:
            if h == 576:
                return Primaries.BT470BG

            return Primaries.ST170M

        if w <= 2048 and h <= 1536:
            return Primaries.BT709

        return Primaries.BT2020

    @classmethod
    def from_video(
        cls, src: vs.VideoNode | vs.VideoFrame | vs.FrameProps, strict: bool = False, func: FuncExceptT | None = None
    ) -> Primaries:
        return _base_from_video(cls, src, UndefinedPrimariesError, strict, func)

    @classmethod
    def from_matrix(cls, matrix: Matrix, strict: bool = False) -> Primaries:
        if matrix not in _matrix_primaries_map:
            if strict:
                raise UnsupportedMatrixError(f'{matrix} is not supported!', cls.from_matrix)

            return cls(matrix.value)

        return _matrix_primaries_map[matrix]

    @classmethod
    def from_transfer(cls, transfer: Transfer, strict: bool = False) -> Primaries:
        if transfer not in _transfer_primaries_map:
            if strict:
                raise UnsupportedTransferError(f'{transfer} is not supported!', cls.from_transfer)

            return cls(transfer.value)

        return _transfer_primaries_map[transfer]

    @property
    def pretty_string(self) -> str:
        return _primaries_pretty_name_map.get(self, super().pretty_string)

    @property
    def string(self) -> str:
        return _primaries_name_map.get(self, super().string)


class MatrixCoefficients(NamedTuple):
    k0: float
    phi: float
    alpha: float
    gamma: float

    @classproperty
    def SRGB(cls) -> MatrixCoefficients:
        return MatrixCoefficients(0.04045, 12.92, 0.055, 2.4)

    @classproperty
    def BT709(cls) -> MatrixCoefficients:
        return MatrixCoefficients(0.08145, 4.5, 0.0993, 2.22222)

    @classproperty
    def SMPTE240M(cls) -> MatrixCoefficients:
        return MatrixCoefficients(0.0912, 4.0, 0.1115, 2.22222)

    @classproperty
    def BT2020(cls) -> MatrixCoefficients:
        return MatrixCoefficients(0.08145, 4.5, 0.0993, 2.22222)

    @classmethod
    def from_matrix(cls, matrix: Matrix) -> MatrixCoefficients:
        if matrix not in _matrix_matrixcoeff_map:
            raise UnsupportedMatrixError(f'{matrix} is not supported!', cls.from_matrix)

        return _matrix_matrixcoeff_map[matrix]

    @classmethod
    def from_transfer(cls, tranfer: Transfer) -> MatrixCoefficients:
        if tranfer not in _transfer_matrixcoeff_map:
            raise UnsupportedTransferError(f'{tranfer} is not supported!', cls.from_transfer)

        return _transfer_matrixcoeff_map[tranfer]

    @classmethod
    def from_primaries(cls, primaries: Primaries) -> MatrixCoefficients:
        if primaries not in _primaries_matrixcoeff_map:
            raise UnsupportedPrimariesError(f'{primaries} is not supported!', cls.from_primaries)

        return _primaries_matrixcoeff_map[primaries]


class ColorRange(_ColorRangeMeta):
    """Full or limited range (PC/TV range). Primarily used with YUV formats."""

    _value_: int

    @classmethod
    def _missing_(cls: type[ColorRange], value: Any) -> ColorRange | None:
        value = super()._missing_(value)

        if value is None:
            return ColorRange.LIMITED
        elif isinstance(value, cls):
            return value

        if value > ColorRange.LIMITED:
            raise UnsupportedPrimariesError(f'ColorRange({value}) is unsupported.', cls)

        return None

    LIMITED = 1
    FULL = 0

    @classmethod
    def from_video(
        cls, src: vs.VideoNode | vs.VideoFrame | vs.FrameProps, strict: bool = False, func: FuncExceptT | None = None
    ) -> ColorRange:
        from ..utils import get_prop

        return get_prop(src, '_ColorRange', int, ColorRange, MISSING if strict else ColorRange.LIMITED)

    @property
    def value_vs(self) -> int:
        return self.value

    @property
    def value_zimg(self) -> int:
        return ~self.value + 2

    @property
    def is_limited(self) -> bool:
        return bool(self.value)

    @property
    def is_full(self) -> bool:
        return not self.value


_transfer_matrix_map: dict[Transfer, Matrix] = {}

_primaries_matrix_map: dict[Primaries, Matrix] = {}

_matrix_transfer_map = {
    Matrix.RGB: Transfer.SRGB,
    Matrix.BT709: Transfer.BT709,
    Matrix.BT470BG: Transfer.BT601,
    Matrix.SMPTE170M: Transfer.BT601,
    Matrix.SMPTE240M: Transfer.ST240M,
    Matrix.CHROMA_DERIVED_C: Transfer.SRGB,
    Matrix.ICTCP: Transfer.BT2020_10bits,
}

_primaries_transfer_map: dict[Primaries, Transfer] = {}

_matrix_primaries_map: dict[Matrix, Primaries] = {}

_transfer_primaries_map: dict[Transfer, Primaries] = {}

_matrix_matrixcoeff_map = {
    Matrix.RGB: MatrixCoefficients.SRGB,
    Matrix.BT709: MatrixCoefficients.BT709,
    Matrix.BT470BG: MatrixCoefficients.BT709,
    Matrix.SMPTE240M: MatrixCoefficients.SMPTE240M,
    Matrix.BT2020C: MatrixCoefficients.BT2020,
    Matrix.BT2020NC: MatrixCoefficients.BT2020
}

_transfer_matrixcoeff_map = {
    Transfer.SRGB: MatrixCoefficients.SRGB,
    Transfer.BT709: MatrixCoefficients.BT709,
    Transfer.BT601: MatrixCoefficients.BT709,
    Transfer.ST240M: MatrixCoefficients.SMPTE240M,
    Transfer.BT2020_10bits: MatrixCoefficients.BT2020,
    Transfer.BT2020_12bits: MatrixCoefficients.BT2020
}

_primaries_matrixcoeff_map = {
    Primaries.BT709: MatrixCoefficients.BT709,
    Primaries.BT470BG: MatrixCoefficients.BT709,
    Primaries.ST240M: MatrixCoefficients.SMPTE240M,
    Primaries.BT2020: MatrixCoefficients.BT2020
}

_transfer_placebo_map = {
    Transfer.UNKNOWN: 0,
    Transfer.BT601_525: 1,
    Transfer.BT601_625: 2,
    Transfer.BT709: 3,
    Transfer.BT470M: 4,
    Transfer.EBU_3213: 5,
    Transfer.BT2020_10bits: 6,
    Transfer.BT2020_12bits: 6,
    Transfer.APPLE: 7,
    Transfer.ADOBE: 8,
    Transfer.PRO_PHOTO: 9,
    Transfer.CIE_1931: 10,
    Transfer.DCI_P3: 11,
    Transfer.DISPLAY_P3: 12,
    Transfer.V_GAMUT: 13,
    Transfer.S_GAMUT: 14,
    Transfer.FILM_C: 15
}

_placebo_transfer_map = {
    value: key for key, value in _transfer_placebo_map.items()
}

_matrix_name_map = {
    Matrix.RGB: 'gbr',
    Matrix.BT709: 'bt709',
    Matrix.UNKNOWN: 'unknown',
    Matrix.FCC: 'fcc',
    Matrix.BT470BG: 'bt470bg',
    Matrix.SMPTE170M: 'smpte170m',
    Matrix.SMPTE240M: 'smpte240m',
    Matrix.BT2020NC: 'bt2020nc',
    Matrix.BT2020C: 'bt2020c',
    Matrix.SMPTE2085: 'smpte2085',
    Matrix.CHROMA_DERIVED_NC: 'chroma-derived-nc',
    Matrix.CHROMA_DERIVED_C: 'chroma-derived-c',
    Matrix.ICTCP: 'ictcp'
}

_transfer_name_map = {
    Transfer.BT709: 'bt709',
    Transfer.UNKNOWN: 'unknown',
    Transfer.BT470M: 'bt470m',
    Transfer.BT470BG: 'bt470bg',
    Transfer.BT601: 'smpte170m',
    Transfer.ST240M: 'smpte240m',
    Transfer.LINEAR: 'linear',
    Transfer.LOG_100: 'log100',
    Transfer.LOG_316: 'log316',
    Transfer.XVYCC: 'iec61966-2-4',
    Transfer.SRGB: 'iec61966-2-1',
    Transfer.BT2020_10bits: 'bt2020-10',
    Transfer.BT2020_12bits: 'bt2020-12',
    Transfer.ST2084: 'smpte2084',
    Transfer.ARIB_B67: 'arib-std-b67'
}


_primaries_name_map = {
    Primaries.BT709: 'bt709',
    Primaries.UNKNOWN: 'unknown',
    Primaries.BT470M: 'bt470m',
    Primaries.BT470BG: 'bt470bg',
    Primaries.ST170M: 'smpte170m',
    Primaries.ST240M: 'smpte240m',
    Primaries.FILM: 'film',
    Primaries.BT2020: 'bt2020',
    Primaries.ST428: 'smpte428',
    Primaries.ST431_2: 'smpte431',
    Primaries.ST432_1: 'smpte432',
    Primaries.EBU3213E: 'jedec-p22'
}

_matrix_pretty_name_map = {
    Matrix.RGB: 'RGB',
    Matrix.BT709: 'BT.709',
    Matrix.FCC: 'FCC',
    Matrix.BT470BG: 'BT.470bg',
    Matrix.SMPTE170M: 'ST 170M',
    Matrix.SMPTE240M: 'ST 240M',
    Matrix.BT2020NC: 'BT.2020 non-constant luminance',
    Matrix.BT2020C: 'BT.2020 constant luminance',
    Matrix.SMPTE2085: 'ST 2085',
    Matrix.CHROMA_DERIVED_NC: 'Chromaticity derived non-constant luminance',
    Matrix.CHROMA_DERIVED_C: 'Chromaticity derived constant luminance',
    Matrix.ICTCP: 'ICtCp'
}

_transfer_pretty_name_map = {
    Transfer.BT709: 'BT.709',
    Transfer.BT470M: 'BT.470m',
    Transfer.BT470BG: 'BT.470bg',
    Transfer.BT601: 'BT.601',
    Transfer.ST240M: 'ST 240M',
    Transfer.LINEAR: 'Linear',
    Transfer.LOG_100: 'Log 1:100 contrast',
    Transfer.LOG_316: 'Log 1:316 contrast',
    Transfer.XVYCC: 'xvYCC',
    Transfer.SRGB: 'sRGB',
    Transfer.BT2020_10bits: 'BT.2020_10',
    Transfer.BT2020_12bits: 'BT.2020_12',
    Transfer.ST2084: 'ST 2084 (PQ)',
    Transfer.ARIB_B67: 'ARIB std-b67 (HLG)'
}

_primaries_pretty_name_map = {
    Primaries.BT709: 'BT.709',
    Primaries.BT470M: 'BT.470m',
    Primaries.BT470BG: 'BT.470bg',
    Primaries.ST170M: 'ST 170M',
    Primaries.ST240M: 'ST 240M',
    Primaries.FILM: 'Film',
    Primaries.BT2020: 'BT.2020',
    Primaries.ST428: 'ST 428 (XYZ)',
    Primaries.ST431_2: 'DCI-P3, DCI white point',
    Primaries.ST432_1: 'DCI-P3 D65 white point',
    Primaries.EBU3213E: '0JEDEC P22 (EBU3213)'
}


MatrixT: TypeAlias = Union[int, vs.MatrixCoefficients, Matrix]
TransferT: TypeAlias = Union[int, vs.TransferCharacteristics, Transfer]
PrimariesT: TypeAlias = Union[int, vs.ColorPrimaries, Primaries]
ColorRangeT: TypeAlias = Union[int, vs.ColorRange, ColorRange]
