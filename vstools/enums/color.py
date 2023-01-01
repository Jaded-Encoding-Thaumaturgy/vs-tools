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
    """Matrix coefficients ([ITU-T H.265](https://www.itu.int/rec/T-REC-H.265) Table E.5)."""

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
                'Matrix YCGCO is no longer supported by VapourSynth starting from R55 (APIv4).', 'Matrix'
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
    """
    ```
    # Identity
    ```\n
    The identity matrix.\n
    Typically used for GBR (often referred to as RGB); however, may also be\n
    used for YZX (often referred to as XYZ)\n
    IEC 61966-2-1 sRGB\n
    SMPTE ST 428-1 (2006)\n
    See ITU-T H.265 Equations E-31 to E-33
    """

    GBR = RGB
    BT709 = 1
    """
    ```
    Kr = 0.2126; Kb = 0.0722
    ```\n
    Rec. ITU-R BT.709-6\n
    Rec. ITU-R BT.1361-0 conventional colour gamut system and extended\n
    colour gamut system (historical)\n
    IEC 61966-2-4 xvYCC709\n
    SMPTE RP 177 (1993) Annex B
    """

    UNKNOWN = 2
    """Image characteristics are unknown or are determined by the application."""

    FCC = 4
    """
    ```
    KR = 0.30; KB = 0.11
    ```\n
    FCC Title 47 Code of Federal Regulations (2003) 73.682 (a) (20)\n
    See ITU-T H.265 Equations E-28 to E-30
    """

    BT470BG = 5
    """
    ```
    KR = 0.299; KB = 0.114
    ```\n
    (Functionally the same as :py:attr:`Matrix.SMPTE170M`)\n
    Rec. ITU-R BT.470-6 System B, G (historical)\n
    Rec. ITU-R BT.601-7 625\n
    Rec. ITU-R BT.1358-0 625 (historical)\n
    Rec. ITU-R BT.1700-0 625 PAL and 625 SECAM\n
    IEC 61966-2-1 sYCC\n
    IEC 61966-2-4 xvYCC601\n
    See ITU-T H.265 Equations E-28 to E-30
    """
    BT601 = BT470BG

    SMPTE170M = 6
    """
    ```
    Kr = 0.299; Kb = 0.114
    ```
    (Functionally the same as :py:attr:`Matrix.BT470BG`)\n
    Rec. ITU-R BT.601-7 525\n
    Rec. ITU-R BT.1358-1 525 or 625 (historical)\n
    Rec. ITU-R BT.1700-0 NTSC\n
    SMPTE ST 170 (2004)\n
    See ITU-T H.265 Equations E-28 to E-30
    """

    SMPTE240M = 7
    """
    ```
    KR = 0.212; KB = 0.087
    ```\n
    SMPTE ST 240 (1999, historical)\n
    See ITU-T H.265 Equations E-28 to E-30
    """

    BT2020NC = 9
    """
    ```
    KR = 0.2627; KB = 0.0593
    ```\n
    Rec. ITU-R BT.2020-2 non-constant luminance system\n
    Rec. ITU-R BT.2100-2 Y′CbCr\n
    See ITU-T H.265 Equations E-28 to E-30
    """

    BT2020C = 10
    """
    ```
    KR = 0.2627; KB = 0.0593
    ```\n
    Rec. ITU-R BT.2020-2 constant luminance system\n
    See ITU-T H.265 Equations E-49 to E-58
    """

    SMPTE2085 = 11
    """
    ```
    # Y′D′ZD′X
    ```\n
    SMPTE ST 2085 (2015)\n
    See ITU-T H.265 Equations E-59 to E-61
    """

    CHROMA_DERIVED_NC = 12
    """
    ```
    # See ITU-T H.265 Equations E-22 to E-27
    ```\n
    Chromaticity-derived non-constant luminance system\n
    See ITU-T H.265 Equations E-28 to E-30

    """

    CHROMA_DERIVED_C = 13
    """
    ```
    # See ITU-T H.265 Equations E-22 to E-27
    ```\n
    Chromaticity-derived constant luminance system\n
    See ITU-T H.265 Equations E-49 to E-58
    """

    ICTCP = 14
    """
    ```
    ICtCp
    ```\n
    Rec. ITU-R BT.2100-2 ICTCP\n
    See ITU-T H.265 Equations E-62 to E-64 for `transfer_characteristics` value 16 (PQ)\n
    See ITU-T H.265 Equations E-65 to E-67 for `transfer_characteristics` value 18 (HLG)
    """

    @classmethod
    def is_unknown(cls, value: int | Matrix) -> bool:
        """Check if Matrix is unknown."""

        return value == cls.UNKNOWN

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
    def from_video(
        cls, src: vs.VideoNode | vs.VideoFrame | vs.FrameProps, strict: bool = False, func: FuncExceptT | None = None
    ) -> Matrix:
        """
        Obtain the matrix of a clip from the frame properties.

        :param src:                         Input clip, frame, or props.
        :param strict:                      Be strict about the properties.
                                            The result may NOT be Matrix.UNKNOWN.

        :return:                            Matrix object.

        :raises UndefinedMatrixError:       Matrix is undefined.
        :raises UndefinedMatrixError:       Matrix can not be determined from the frameprops.
        """

        return _base_from_video(cls, src, UndefinedMatrixError, strict, func)

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

    @property
    def pretty_string(self) -> str:
        return _matrix_pretty_name_map.get(self, super().pretty_string)

    @property
    def string(self) -> str:
        return _matrix_name_map.get(self, super().string)


class Transfer(_TransferMeta):
    """Transfer characteristics ([ITU-T H.265](https://www.itu.int/rec/T-REC-H.265) Table E.4)."""

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
    """
    (Functionally the same as :py:attr:`Transfer.BT601`, :py:attr:`Transfer.BT2020_10bits`,
    and :py:attr:`Transfer.BT2020_12bits`)\n
    Rec. ITU-R BT.709-6\n
    Rec. ITU-R BT.1361-0 conventional\n
    Colour gamut system (historical)
    """

    UNKNOWN = 2
    """Image characteristics are unknown or are determined by the application."""

    BT470M = 4
    """
    Rec. ITU-R BT.470-6 System M (historical)\n
    NTSC Recommendation for transmission standards for colour television (1953)\n
    FCC, Title 47 Code of Federal Regulations (2003) 73.682 (a) (20)
    """

    BT470BG = 5
    """
    Rec. ITU-R BT.470-6 System B, G (historical)\n
    Rec. ITU-R BT.1700-0 625 PAL and\n
    625 SECAM
    """

    BT601 = 6
    """
    (Functionally the same as :py:attr:`Transfer.BT701`, :py:attr:`Transfer.BT2020_10bits`,
    and :py:attr:`Transfer.BT2020_12bits`)\n
    Rec. ITU-R BT.601-7 525 or 625\n
    Rec. ITU-R BT.1358-1 525 or 625 (historical)\n
    Rec. ITU-R BT.1700-0 NTSC\n
    SMPTE ST 170 (2004)
    """

    ST240M = 7
    """SMPTE ST 240 (1999, historical)"""

    LINEAR = 8
    """Linear transfer characteristics"""

    LOG_100 = 9
    """Logarithmic transfer characteristic (100:1 range)"""

    LOG_316 = 10
    """Logarithmic transfer characteristic (100 * sqrt(10):1 range)"""

    XVYCC = 11
    """IEC 61966-2-4"""

    SRGB = 13
    """
    IEC 61966-2-1 sRGB when matrix is equal to :py:attr:`Matrix.RGB`\n
    IEC 61966-2-1 sYCC when matrix is equal to :py:attr:`Matrix.BT470BG`
    """

    BT2020_10bits = 14
    """
    (Functionally the same as :py:attr:`Transfer.BT701`, :py:attr:`Transfer.BT601`,
    and :py:attr:`Transfer.BT2020_12bits`)\n
    Rec. ITU-R BT.2020-2

    """

    BT2020_12bits = 15
    """
    (Functionally the same as :py:attr:`Transfer.BT701`, :py:attr:`Transfer.BT601`,
    and :py:attr:`Transfer.BT2020_10bits`)\n
    Rec. ITU-R BT.2020-2
    """

    ST2084 = 16
    """
    SMPTE ST 2084 (2014) for 10, 12, 14, and 16-bit systems\n
    Rec. ITU-R BT.2100-2 perceptual quantization (PQ) system
    """

    ARIB_B67 = 18
    """
    Association of Radio Industries and Businesses (ARIB) STD-B67\n
    Rec. ITU-R BT.2100-2 hybrid loggamma (HLG) system
    """

    """
    Extra tranfer characterists from libplacebo
    https://github.com/haasn/libplacebo/blob/master/src/include/libplacebo/colorspace.h#L193
    """

    # Standard gamut:
    BT601_525 = 100
    """ITU-R Rec. BT.601 (525-line = NTSC, SMPTE-C)"""

    BT601_625 = 101
    """ITU-R Rec. BT.601 (625-line = PAL, SECAM)"""

    EBU_3213 = 102
    """EBU Tech. 3213-E / JEDEC P22 phosphors"""

    # Wide gamut:
    APPLE = 103
    """Apple RGB"""

    ADOBE = 104
    """Adobe RGB (1998)"""

    PRO_PHOTO = 105
    """ProPhoto RGB (ROMM)"""

    CIE_1931 = 106
    """CIE 1931 RGB primaries"""

    DCI_P3 = 107
    """DCI-P3 (Digital Cinema)"""

    DISPLAY_P3 = 108
    """DCI-P3 (Digital Cinema) with D65 white point"""

    V_GAMUT = 109
    """Panasonic V-Gamut (VARICAM)"""

    S_GAMUT = 110
    """Sony S-Gamut"""

    FILM_C = 111
    """Traditional film primaries with Illuminant C"""

    @classmethod
    def is_unknown(cls, value: int | Transfer) -> bool:
        """Check if Transfer is unknown."""

        return value == cls.UNKNOWN

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
    def from_video(
        cls, src: vs.VideoNode | vs.VideoFrame | vs.FrameProps, strict: bool = False, func: FuncExceptT | None = None
    ) -> Transfer:
        """
        Obtain the transfer of a clip from the frame properties.

        :param src:                         Input clip, frame, or props.
        :param strict:                      Be strict about the properties.
                                            The result may NOT be Transfer.UNKNOWN.

        :return:                            Transfer object.

        :raises UndefinedTransferError:     Transfer is undefined.
        :raises UndefinedTransferError:     Transfer can not be determined from the frameprops.
        """

        return _base_from_video(cls, src, UndefinedTransferError, strict, func)

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

    @property
    def pretty_string(self) -> str:
        return _transfer_pretty_name_map.get(self, super().pretty_string)

    @property
    def string(self) -> str:
        return _transfer_name_map.get(self, super().string)


class Primaries(_PrimariesMeta):
    """Color primaries ([ITU-T H.265](https://www.itu.int/rec/T-REC-H.265) Table E.3)."""

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
    """
    ```
    Primary      x      y
    Green     0.3000 0.6000
    Blue      0.1500 0.0600
    Red       0.6400 0.3300
    White D65 0.3127 0.3290
    ```

    Rec. ITU-R BT.709-6
    Rec. ITU-R BT.1361-0 conventional colour gamutsystem and extended colour gamut system (historical)
    IEC 61966-2-1 sRGB or sYCC
    IEC 61966-2-4
    SMPTE RP 177 (1993) Annex B
    """

    UNKNOWN = 2
    """Unspecified Image characteristics are unknown or are determined by the application."""

    BT470M = 4
    """
    ```
    Primary     x      y
    Green    0.2100 0.7100
    Blue     0.1400 0.0800
    Red      0.6700 0.3300
    White C  0.3100 0.3160
    ```

    Rec. ITU-R BT.470-6 System M (historical)
    NTSC Recommendation for transmission
    standards for colour television (1953)
    FCC Title 47 Code of Federal Regulations (2003)
    73.682 (a) (20)
    """

    BT470BG = 5
    """
    ```
    Primary      x      y
    Green     0.2900 0.6000
    Blue      0.1500 0.0600
    Red       0.6400 0.3300
    White D65 0.3127 0.3290
    ```

    Rec. ITU-R BT.470-6 System B, G (historical)
    Rec. ITU-R BT.601-7 625
    Rec. ITU-R BT.1358-0 625 (historical)
    Rec. ITU-R BT.1700-0 625 PAL and 625
    SECAM
    """

    ST170M = 6
    """
    (Functionally the same as :py:attr:`Primaries.ST240M`)
    ```
    Primary      x      y
    Green     0.3100 0.5950
    Blue      0.1550 0.0700
    Red       0.6300 0.3400
    White D65 0.3127 0.3290
    ```

    Rec. ITU-R BT.601-7 525
    Rec. ITU-R BT.1358-1 525 or 625 (historical)
    Rec. ITU-R BT.1700-0 NTSC
    SMPTE ST 170 (2004)
    """

    ST240M = 7
    """
    (Functionally the same as :py:attr:`Primaries.ST170M`)
    ```
    Primary      x      y
    Green     0.3100 0.5950
    Blue      0.1550 0.0700
    Red       0.6300 0.3400
    White D65 0.3127 0.3290
    ```

    SMPTE ST 240 (1999, historical)
    """

    FILM = 8
    """
    ```
    Primary    x      y
    Green   0.2430 0.6920 #(Wratten 58)
    Blue    0.1450 0.0490 #(Wratten 47)
    Red     0.6810 0.3190 #(Wratten 25)
    White C 0.3100 0.3160
    ```

    Generic film (colour filters using Illuminant C)
    """

    BT2020 = 9
    """
    ```
    Primary       x      y
    Green     0.1700 0.7970
    Blue      0.1310 0.0460
    Red       0.7080 0.2920
    White D65 0.3127 0.3290
    ```

    Rec. ITU-R BT.2020-2\n
    Rec. ITU-R BT.2100-2
    """

    ST428 = 10
    """
    ```
    Primary        x   y
    Green    (Y)  0.0 1.0
    Blue     (Z)  0.0 0.0
    Red      (X)  1.0 0.0
    Centre White  1/3 1/3
    ```

    SMPTE ST 428-1 (2006)\n
    (CIE 1931 XYZ)
    """
    XYZ = ST428

    ST431_2 = 11
    """
    ```
    Primary    x      y
    Green   0.2650 0.6900
    Blue    0.1500 0.0600
    Red     0.6800 0.3200
    White   0.3140 0.3510
    ```

    SMPTE RP 431-2 (2011)\n
    SMPTE ST 2113 (2019) "P3DCI"
    """

    ST432_1 = 12
    """
    ```
    Primary      x      y
    Green     0.2650 0.6900
    Blue      0.1500 0.0600
    Red       0.6800 0.3200
    White D65 0.3127 0.3290
    ```

    SMPTE EG 432-1 (2010)\n
    SMPTE ST 2113 (2019) "P3D65"
    """

    EBU3213E = 22
    """
    ```
    Primary      x      y
    Green     0.2950 0.6050
    Blue      0.1550 0.0770
    Red       0.6300 0.3400
    White D65 0.3127 0.3290
    ```

    EBU Tech. 3213-E (1975)
    """

    @classmethod
    def is_unknown(cls, value: int | Primaries) -> bool:
        """Check if Primaries is unknown."""

        return value == cls.UNKNOWN

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
    def from_video(
        cls, src: vs.VideoNode | vs.VideoFrame | vs.FrameProps, strict: bool = False, func: FuncExceptT | None = None
    ) -> Primaries:
        """
        Obtain the primaries of a clip from the frame properties.

        :param src:                         Input clip, frame, or props.
        :param strict:                      Be strict about the properties.
                                            The result may NOT be Primaries.UNKNOWN.

        :return:                            Primaries object.

        :raises UndefinedPrimariesError:    Primaries is undefined.
        :raises UndefinedPrimariesError:    Primaries can not be determined from the frame properties.
        """

        return _base_from_video(cls, src, UndefinedPrimariesError, strict, func)

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

    @property
    def pretty_string(self) -> str:
        return _primaries_pretty_name_map.get(self, super().pretty_string)

    @property
    def string(self) -> str:
        return _primaries_name_map.get(self, super().string)


class MatrixCoefficients(NamedTuple):
    """Class representing Linear <-> Gamma conversion matrix coefficients."""

    k0: float
    """Coefficient representing the offset of the linear value relative to the gamma value."""

    phi: float
    """Coefficient representing the slope of the linear value relative to the gamma value."""

    alpha: float
    """Coefficient representing the non-linearity of the gamma curve."""

    gamma: float
    """Coefficient representing the exponent of the gamma curve."""

    @classproperty
    def SRGB(cls) -> MatrixCoefficients:
        """Matrix Coefficients for SRGB."""

        return MatrixCoefficients(0.04045, 12.92, 0.055, 2.4)

    @classproperty
    def BT709(cls) -> MatrixCoefficients:
        """Matrix Coefficients for BT709."""

        return MatrixCoefficients(0.08145, 4.5, 0.0993, 2.22222)

    @classproperty
    def SMPTE240M(cls) -> MatrixCoefficients:
        """Matrix Coefficients for SMPTE240M."""

        return MatrixCoefficients(0.0912, 4.0, 0.1115, 2.22222)

    @classproperty
    def BT2020(cls) -> MatrixCoefficients:
        """Matrix Coefficients for BT2020."""

        return MatrixCoefficients(0.08145, 4.5, 0.0993, 2.22222)

    @classmethod
    def from_matrix(cls, matrix: Matrix) -> MatrixCoefficients:
        """Matrix Coefficients from a Matrix object's value."""

        if matrix not in _matrix_matrixcoeff_map:
            raise UnsupportedMatrixError(f'{matrix} is not supported!', cls.from_matrix)

        return _matrix_matrixcoeff_map[matrix]

    @classmethod
    def from_transfer(cls, tranfer: Transfer) -> MatrixCoefficients:
        """Matrix Coefficients from a Transfer object's value."""

        if tranfer not in _transfer_matrixcoeff_map:
            raise UnsupportedTransferError(f'{tranfer} is not supported!', cls.from_transfer)

        return _transfer_matrixcoeff_map[tranfer]

    @classmethod
    def from_primaries(cls, primaries: Primaries) -> MatrixCoefficients:
        """Matrix Coefficients from a Primaries object's value."""

        if primaries not in _primaries_matrixcoeff_map:
            raise UnsupportedPrimariesError(f'{primaries} is not supported!', cls.from_primaries)

        return _primaries_matrixcoeff_map[primaries]


class ColorRange(_ColorRangeMeta):
    """Pixel Range ([ITU-T H.265](https://www.itu.int/rec/T-REC-H.265) Equations E-10 through E-20."""

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
    """
    Studio (TV) legal range, 16-235 in 8 bits.

    | This is primarily used with YUV integer formats.
    """

    FULL = 0
    """
    Full (PC) dynamic range, 0-255 in 8 bits.


    | Note that float clips should always be FULL range!\n
    | RGB clips will always be FULL range!
    """

    @classmethod
    def from_video(
        cls, src: vs.VideoNode | vs.VideoFrame | vs.FrameProps, strict: bool = False, func: FuncExceptT | None = None
    ) -> ColorRange:
        """
        Obtain the color range of a clip from the frame properties.

        :param src:                         Input clip, frame, or props.
        :param strict:                      Be strict about the properties.
                                            Sets the ColorRange as MISSING if prop is not there.

        :return:                            ColorRange object.
        """

        from ..utils import get_prop

        return get_prop(src, '_ColorRange', int, ColorRange, MISSING if strict else ColorRange.LIMITED)

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
"""Type alias for values that can be used to initialize a :py:attr:`Matrix`."""

TransferT: TypeAlias = Union[int, vs.TransferCharacteristics, Transfer]
"""Type alias for values that can be used to initialize a :py:attr:`Transfer`."""

PrimariesT: TypeAlias = Union[int, vs.ColorPrimaries, Primaries]
"""Type alias for values that can be used to initialize a :py:attr:`Primaries`."""

ColorRangeT: TypeAlias = Union[int, vs.ColorRange, ColorRange]
"""Type alias for values that can be used to initialize a :py:attr:`ColorRange`."""
