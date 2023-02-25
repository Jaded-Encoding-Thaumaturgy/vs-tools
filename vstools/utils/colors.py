from dataclasses import dataclass

import vapoursynth as vs

from ..enums import Matrix
from ..functions import DitherType, check_variable_format, depth, join, plane, split
from ..types import FuncExceptT, inject_self

__all__ = [
    'ResampleUtil'
]


@dataclass
class ResampleUtil:
    fp32: bool | None = None
    """Whether to process in original bitdepth (None) or in int16 (False) or float32 (True)."""

    @inject_self
    def clip2opp(self, clip: vs.VideoNode, is_gray: bool = False, func: FuncExceptT | None = None) -> vs.VideoNode:
        """
        Convert any clip to the OPP colorspace.

        :param clip:    Clip to be processed.
        :param is_gray: Whether to only extract the luma.
        :param func:    Function from where this was called from.

        :return:        OPP clip.
        """
        func = func or self.clip2opp

        assert check_variable_format(clip, func)

        if is_gray:
            return self.to_gray(clip, func)

        return self.rgb2opp(clip, func) if clip.format.color_family is vs.RGB else self.yuv2opp(clip, func)

    @inject_self
    def yuv2opp(self, clip: vs.VideoNode, func: FuncExceptT | None = None) -> vs.VideoNode:
        """
        Convert a YUV clip to the OPP colorspace.

        :param clip:    YUV clip to be processed.
        :param func:    Function from where this was called from.

        :return:        OPP clip.
        """
        return self.rgb2opp(clip.resize.Bicubic(format=vs.RGBS), func)

    @inject_self
    def rgb2opp(self, clip: vs.VideoNode, func: FuncExceptT | None = None) -> vs.VideoNode:
        """
        Convert an RGB clip to the OPP colorspace.

        :param clip:    RGB clip to be processed.
        :param func:    Function from where this was called from.

        :return:        OPP clip.
        """
        assert check_variable_format(clip, (func := func or self.rgb2opp))

        if hasattr(vs.core, 'fmtc'):
            clip = clip.fmtc.matrix(
                fulls=True, fulld=True, col_fam=vs.YUV, coef=[
                    1, 1, 2 / 3, 0, 1, 0, -4 / 3, 0, 1, -1, 2 / 3, 0
                ]
            )
        else:
            from ..utils import get_neutral_value

            diff = '' if clip.format.bits_per_sample == 32 else f'{get_neutral_value(clip)} +'

            R, G, B = split(clip)

            clip = join([
                vs.core.std.Expr([R, G, B], 'x y z + + 1 3 / *'),
                vs.core.std.Expr([R, B], f'x y - 1 2 / * {diff}'),
                vs.core.std.Expr([R, G, B], f'x z + 1 4 / * y 1 2 / * - {diff}')
            ], vs.YUV)

        if self.fp32 is None:
            return clip

        return depth(clip, 32 if self.fp32 else 16)

    @inject_self
    def opp2rgb(self, clip: vs.VideoNode, func: FuncExceptT | None = None) -> vs.VideoNode:
        """
        Convert an OPP clip to the RGB colorspace.

        :param clip:    OPP clip to be processed.
        :param func:    Function from where this was called from.

        :return:        RGB clip.
        """
        assert check_variable_format(clip, (func := func or self.opp2rgb))

        if hasattr(vs.core, 'fmtc'):
            clip = clip.fmtc.matrix(
                fulls=True, fulld=True, col_fam=vs.RGB, coef=[
                    1 / 3, 1 / 3, 1 / 3, 0, 1 / 2, 0, -1 / 2, 0, 1 / 4, -1 / 2, 1 / 4, 0
                ]
            )
        else:
            from ..utils import get_neutral_value

            diff = '' if clip.format.bits_per_sample == 32 else f'{get_neutral_value(clip)} -'

            Y, U, V = split(clip)

            clip = join([
                vs.core.std.Expr([Y, U, V], f'x y {diff} + z {diff} 2 3 / * +'),
                vs.core.std.Expr([Y, V], f'x y {diff} 4 3 / * -'),
                vs.core.std.Expr([Y, U, V], f'x z {diff} 2 3 / * + y {diff} -')
            ], vs.RGB)

        if self.fp32 is None:
            return clip

        return depth(clip, 32 if self.fp32 else 16)

    @inject_self
    def opp2yuv(
        self, clip: vs.VideoNode, format: vs.VideoFormat, matrix: Matrix | None,
        dither: DitherType | None = None, func: FuncExceptT | None = None
    ) -> vs.VideoNode:
        """
        Convert an OPP clip to the YUV colorspace.

        :param clip:    OPP clip to be processed.
        :param func:    Function from where this was called from.

        :return:        YUV clip.
        """
        assert check_variable_format(clip, (func := func or self.opp2yuv))

        return self.opp2rgb(clip, func).resize.Bicubic(format=format.id, matrix=matrix, dither_type=dither)

    @inject_self
    def to_gray(self, clip: vs.VideoNode, func: FuncExceptT | None = None) -> vs.VideoNode:
        """
        Extract Y plane from a clip.

        :param clip:    Clip to be processed.
        :param func:    Function from where this was called from.

        :return:        Gray clip.
        """
        assert check_variable_format(clip, func or self.to_gray)

        if clip.format.color_family is vs.RGB:
            clip = self.rgb2opp(clip, func)

        if self.fp32 is None or (32 if self.fp32 else 16) == clip.format.bits_per_sample:  # type: ignore
            return plane(clip, 0)

        return clip.resize.Point(format=vs.GRAYS if self.fp32 else vs.GRAY16)
