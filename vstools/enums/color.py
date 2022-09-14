from __future__ import annotations

from typing import Any, NamedTuple, TypeAlias

import vapoursynth as vs

from ..exceptions import (
    ReservedMatrixError, ReservedPrimariesError, ReservedTransferError, UndefinedMatrixError, UndefinedPrimariesError,
    UndefinedTransferError, UnsupportedMatrixError, UnsupportedPrimariesError, UnsupportedTransferError
)
from ..types import MISSING
from .stubs import _ColorRangeMeta, _MatrixMeta, _PrimariesMeta, _TransferMeta

__all__ = [
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
        if value is None:
            return Matrix.UNKNOWN

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
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    GBR = RGB
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    BT709 = 1
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    UNKNOWN = 2
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    FCC = 4
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    BT470BG = 5
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    BT601 = BT470BG
    SMPTE170M = 6
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    SMPTE240M = 7
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    BT2020NC = 9
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    BT2020C = 10
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    SMPTE2085 = 11
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    CHROMA_DERIVED_NC = 12
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    CHROMA_DERIVED_C = 13
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    ICTCP = 14
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""

    @property
    def is_unknown(self) -> bool:
        """Check if Matrix is unknown."""
        return self is Matrix.UNKNOWN

    @classmethod
    def from_res(cls, frame: vs.VideoNode | vs.VideoFrame) -> Matrix:
        """
        Guess the matrix based on the clip's resolution.

        :param frame:       Input clip or frame.

        :return:            Matrix object.
        """
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
    def from_video(cls, src: vs.VideoNode | vs.VideoFrame | vs.FrameProps, strict: bool = False) -> Matrix:
        """
        Obtain the matrix of a clip from the frame properties.

        :param src:                         Input clip, frame, or props.
        :param strict:                      Be strict about the properties.
                                            The result may NOT be Matrix.UNKNOWN.

        :return:                            Matrix object.

        :raises UndefinedMatrixError:       Matrix is undefined.
        :raises UndefinedMatrixError:       Matrix can not be determined from the frameprops.
        """
        from ..utils import get_prop

        value = get_prop(src, '_Matrix', int, default=MISSING if strict else None)

        if value is None or value == Matrix.UNKNOWN:
            if strict:
                raise UndefinedMatrixError(f'Matrix({value}) is undefined.', cls.from_video)

            if isinstance(src, vs.FrameProps):
                raise UndefinedMatrixError('Can\'t determine matrix from FrameProps.', cls.from_video)

            return cls.from_res(src)

        return cls(value)

    @classmethod
    def from_transfer(cls, transfer: Transfer, strict: bool = False) -> Matrix:
        """
        Obtain the matrix from a Transfer object.

        :param transfer:                        Transfer object.
        :param strict:                          Be strict about the properties.
                                                The result may NOT be Transfer.UNKNOWN.

        :return:                                Matrix object.

        :raises UnsupportedTransferError:       Transfer is not supported.
        """
        if transfer not in _transfer_matrix_map:
            if strict:
                raise UnsupportedTransferError(f'{transfer} is not supported!', cls.from_transfer)

            return cls(transfer.value)

        return _transfer_matrix_map[transfer]

    @classmethod
    def from_primaries(cls, primaries: Primaries, strict: bool = False) -> Matrix:
        """
        Obtain the matrix from a Primaries object.

        :param transfer:                        Primaries object.
        :param strict:                          Be strict about the properties.
                                                The result may NOT be Primaries.UNKNOWN.

        :return:                                Matrix object.

        :raises UnsupportedPrimariesError:      Primaries is not supported.
        """
        if primaries not in _primaries_matrix_map:
            if strict:
                raise UnsupportedPrimariesError(f'{primaries} is not supported!', cls.from_primaries)

            return cls(primaries.value)

        return _primaries_matrix_map[primaries]


class Transfer(_TransferMeta):
    """Transfer characteristics (ITU-T H.265)."""

    _value_: int

    @classmethod
    def _missing_(cls: type[Transfer], value: Any) -> Transfer | None:
        if value is None:
            return Transfer.UNKNOWN

        if Transfer.BT709 < value < Transfer.ARIB_B67:
            raise ReservedTransferError(f'Transfer({value}) is reserved.', cls)

        if value > Transfer.ARIB_B67:
            raise UnsupportedTransferError(
                f'Transfer({value}) is current unsupported. '
                'If you believe this to be in error, please leave an issue '
                'in the vs-tools GitHub repository.', cls
            )

        return None

    BT709 = 1
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    UNKNOWN = 2
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    BT470M = 4
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    BT470BG = 5
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    BT601 = 6
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    ST240M = 7
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    LINEAR = 8
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    LOG_100 = 9
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    LOG_316 = 10
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    XVYCC = 11
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    SRGB = 13
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    BT2020_10bits = 14
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    BT2020_12bits = 15
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    ST2084 = 16
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    ARIB_B67 = 18
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""

    """
    Extra tranfer characterists from libplacebo
    https://github.com/haasn/libplacebo/blob/master/src/include/libplacebo/colorspace.h#L193
    """

    # Standard gamut:
    BT601_525 = 100
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    BT601_625 = 101
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    EBU_3213 = 102
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    # Wide gamut:
    APPLE = 103
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    ADOBE = 104
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    PRO_PHOTO = 105
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    CIE_1931 = 106
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    DCI_P3 = 107
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    DISPLAY_P3 = 108
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    V_GAMUT = 109
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    S_GAMUT = 110
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    FILM_C = 111
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    COUNT = 112
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""

    @property
    def is_unknown(self) -> bool:
        """Check if Transfer is unknown."""
        return self is Transfer.UNKNOWN

    @classmethod
    def from_res(cls, frame: vs.VideoNode | vs.VideoFrame) -> Transfer:
        """
        Guess the transfer based on the clip's resolution.

        :param frame:       Input clip or frame.

        :return:            Transfer object.
        """
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
    def from_video(cls, src: vs.VideoNode | vs.VideoFrame | vs.FrameProps, strict: bool = False) -> Transfer:
        """
        Obtain the transfer of a clip from the frame properties.

        :param src:                         Input clip, frame, or props.
        :param strict:                      Be strict about the properties.
                                            The result may NOT be Transfer.UNKNOWN.

        :return:                            Transfer object.

        :raises UndefinedTransferError:     Transfer is undefined.
        :raises UndefinedTransferError:     Transfer can not be determined from the frameprops.
        """
        from ..utils import get_prop

        value = get_prop(src, '_Transfer', int, default=MISSING if strict else None)

        if value is None or value == Transfer.UNKNOWN:
            if strict:
                raise UndefinedTransferError(f'Transfer({value}) is undefined.', cls.from_video)

            if isinstance(src, vs.FrameProps):
                raise UndefinedTransferError('Can\'t determine transfer from FrameProps.', cls.from_video)

            return cls.from_res(src)

        return cls(value)

    @classmethod
    def from_matrix(cls, matrix: Matrix, strict: bool = False) -> Transfer:
        """
        Obtain the transfer from a Matrix object.

        :param matrix:                          Matrix object.
        :param strict:                          Be strict about the properties.
                                                The matrix may NOT be Matrix.UNKNOWN!

        :return:                                Transfer object.

        :raises UnsupportedMatrixError:         Matrix is not supported.
        """
        if matrix not in _matrix_transfer_map:
            if strict:
                raise UnsupportedMatrixError(f'{matrix} is not supported!', cls.from_matrix)

            return cls(matrix.value)

        return _matrix_transfer_map[matrix]

    @classmethod
    def from_primaries(cls, primaries: Primaries, strict: bool = False) -> Transfer:
        """
        Obtain the transfer from a Primaries object.

        :param primaries:                       Primaries object.
        :param strict:                          Be strict about the properties.
                                                The matrix may NOT be Primaries.UNKNOWN!

        :return:                                Transfer object.

        :raises UnsupportedPrimariesError:      Primaries is not supported.
        """
        if primaries not in _primaries_transfer_map:
            if strict:
                raise UnsupportedPrimariesError(f'{primaries} is not supported!', cls.from_primaries)

            return cls(primaries.value)

        return _primaries_transfer_map[primaries]

    @classmethod
    def from_libplacebo(self, val: int) -> int:
        """Obtain the transfer from libplacebo."""
        return _placebo_transfer_map[val]

    @property
    def value_vs(self) -> int:
        """
        VapourSynth value.

        :raises ReservedTransferError:      Transfer is not an internal transfer, but a libplacebo one.
        """
        if self >= self.BT601_525:
            raise ReservedTransferError(
                'This transfer isn\'t a VapourSynth internal transfer, but a libplacebo one!',
                f'{self.__class__.__name__}.value_vs'
            )

        return self.value

    @property
    def value_libplacebo(self) -> int:
        """libplacebo value."""
        return _transfer_placebo_map[self]


class Primaries(_PrimariesMeta):
    """Color primaries (ITU-T H.265)."""

    _value_: int

    @classmethod
    def _missing_(cls: type[Primaries], value: Any) -> Primaries | None:
        if value is None:
            return Primaries.UNKNOWN

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
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    UNKNOWN = 2
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    BT470M = 4
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    BT470BG = 5
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    ST170M = 6
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    ST240M = 7
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    FILM = 8
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    BT2020 = 9
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    ST428 = 10
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    ST431_2 = 11
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    ST432_1 = 12
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    EBU3213E = 22
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""

    @property
    def is_unknown(self) -> bool:
        """Check if Primaries is unknown."""
        return self is Primaries.UNKNOWN

    @classmethod
    def from_res(cls, frame: vs.VideoNode | vs.VideoFrame) -> Primaries:
        """
        Guess the primaries based on the clip's resolution.

        :param frame:       Input clip or frame.

        :return:            Primaries object.
        """
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
    def from_video(cls, src: vs.VideoNode | vs.VideoFrame | vs.FrameProps, strict: bool = False) -> Primaries:
        """
        Obtain the primaries of a clip from the frame properties.

        :param src:                         Input clip, frame, or props.
        :param strict:                      Be strict about the properties.
                                            The result may NOT be Primaries.UNKNOWN.

        :return:                            Primaries object.

        :raises UndefinedPrimariesError:    Primaries is undefined.
        :raises UndefinedPrimariesError:    Primaries can not be determined from the frameprops.
        """
        from ..utils import get_prop

        value = get_prop(src, '_Primaries', int, default=MISSING if strict else None)

        if value is None or value == Primaries.UNKNOWN:
            if strict:
                raise UndefinedPrimariesError(f'Primaries({value}) is undefined.', cls.from_video)

            if isinstance(src, vs.FrameProps):
                raise UndefinedPrimariesError('Can\'t determine primaries from FrameProps.', cls.from_video)

            return cls.from_res(src)

        return cls(value)

    @classmethod
    def from_matrix(cls, matrix: Matrix, strict: bool = False) -> Primaries:
        """
        Obtain the primaries from a Matrix object.

        :param matrix:                          Matrix object.
        :param strict:                          Be strict about the properties.
                                                The matrix may NOT be Matrix.UNKNOWN!

        :return:                                Primaries object.

        :raises UnsupportedMatrixError:         Matrix is not supported.
        """
        if matrix not in _matrix_primaries_map:
            if strict:
                raise UnsupportedMatrixError(f'{matrix} is not supported!', cls.from_matrix)

            return cls(matrix.value)

        return _matrix_primaries_map[matrix]

    @classmethod
    def from_transfer(cls, transfer: Transfer, strict: bool = False) -> Primaries:
        """
        Obtain the primaries from a Transfer object.

        :param transfer:                        Transfer object.
        :param strict:                          Be strict about the properties.
                                                The result may NOT be Transfer.UNKNOWN.

        :return:                                Matrix object.

        :raises UnsupportedTransferError:       Transfer is not supported.
        """
        if transfer not in _transfer_primaries_map:
            if strict:
                raise UnsupportedTransferError(f'{transfer} is not supported!', cls.from_transfer)

            return cls(transfer.value)

        return _transfer_primaries_map[transfer]


class MatrixCoefficients(NamedTuple):
    """Class representing Linear <-> Gamma conversion matrix coefficients"""

    k0: float
    phi: float
    alpha: float
    gamma: float

    @classmethod
    @property
    def SRGB(cls) -> MatrixCoefficients:
        """Matrix Coefficients for SRGB."""
        return MatrixCoefficients(0.04045, 12.92, 0.055, 2.4)

    @classmethod
    @property
    def BT709(cls) -> MatrixCoefficients:
        """Matrix Coefficients for BT709."""
        return MatrixCoefficients(0.08145, 4.5, 0.0993, 2.22222)

    @classmethod
    @property
    def SMPTE240M(cls) -> MatrixCoefficients:
        """Matrix Coefficients for SMPTE240M."""
        return MatrixCoefficients(0.0912, 4.0, 0.1115, 2.22222)

    @classmethod
    @property
    def BT2020(cls) -> MatrixCoefficients:
        """Matrix Coefficients for BT2020."""
        return MatrixCoefficients(0.08145, 4.5, 0.0993, 2.22222)

    @classmethod
    def from_matrix(cls, matrix: Matrix) -> MatrixCoefficients:
        """Matrix Coefficients from a Matrix object's value."""
        if matrix not in _matrix_matrixcoeff_map:
            raise UnsupportedMatrixError(f'{matrix} is not supported!', cls.from_matrix)

        return _matrix_matrixcoeff_map[matrix]  # type: ignore

    @classmethod
    def from_transfer(cls, tranfer: Transfer) -> MatrixCoefficients:
        """Matrix Coefficients from a Transfer object's value."""
        if tranfer not in _transfer_matrixcoeff_map:
            raise UnsupportedTransferError(f'{tranfer} is not supported!', cls.from_transfer)

        return _transfer_matrixcoeff_map[tranfer]  # type: ignore

    @classmethod
    def from_primaries(cls, primaries: Primaries) -> MatrixCoefficients:
        """Matrix Coefficients from a Primaries object's value."""
        if primaries not in _primaries_matrixcoeff_map:
            raise UnsupportedPrimariesError(f'{primaries} is not supported!', cls.from_primaries)

        return _primaries_matrixcoeff_map[primaries]  # type: ignore


class ColorRange(_ColorRangeMeta):
    """Full or limited range (PC/TV range). Primarily used with YUV formats."""

    _value_: int

    @classmethod
    def _missing_(cls: type[ColorRange], value: Any) -> ColorRange | None:
        if value is None:
            return ColorRange.LIMITED

        if value > ColorRange.LIMITED:
            raise UnsupportedPrimariesError(f'ColorRange({value}) is unsupported.', cls)

        return None

    LIMITED = 1
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
    FULL = 0
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""

    @property
    def is_unknown(self) -> bool:
        """Check if ColorRange is unknown."""
        return False

    @classmethod
    def from_video(cls, src: vs.VideoNode | vs.VideoFrame | vs.FrameProps, strict: bool = False) -> ColorRange:
        """
        Obtain the color range of a clip from the frame properties.

        :param src:                         Input clip, frame, or props.
        :param strict:                      Be strict about the properties.
                                            Sets the ColorRange as MISSING if prop is not there.

        :return:                            ColorRange object.
        """
        from ..utils import get_prop

        return get_prop(
            src, '_ColorRange', int, ColorRange, MISSING if strict else ColorRange.LIMITED
        )

    @property
    def value_vs(self) -> int:
        """VapourSynth (props) value."""
        return self.value

    @property
    def value_zimg(self) -> int:
        """zimg (resize plugin) value."""
        return ~self.value + 2

    @property
    def is_limited(self) -> bool:
        """Check if ColorRange is limited."""
        return bool(self.value)

    @property
    def is_full(self) -> bool:
        """Check if ColorRange is full."""
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
    Transfer.FILM_C: 15,
    Transfer.COUNT: 16
}

_placebo_transfer_map = {
    value: key for key, value in _transfer_placebo_map.items()
}

MatrixT: TypeAlias = int | vs.MatrixCoefficients | Matrix
"""@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""

TransferT: TypeAlias = int | vs.TransferCharacteristics | Transfer
"""@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""

PrimariesT: TypeAlias = int | vs.ColorPrimaries | Primaries
"""@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""

ColorRangeT: TypeAlias = int | vs.ColorRange | ColorRange
"""@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
