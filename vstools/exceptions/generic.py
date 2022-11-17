from __future__ import annotations

from fractions import Fraction
from typing import Any, Iterable

import vapoursynth as vs

from ..types import FuncExceptT, HoldsVideoFormatT, SupportsString, VideoFormatT
from .base import CustomKeyError, CustomOverflowError, CustomValueError

__all__ = [
    'FramesLengthError', 'ClipLengthError',

    'VariableFormatError', 'VariableResolutionError',

    'FormatsMismatchError', 'FormatsRefClipMismatchError',

    'ResolutionsMismatchError', 'ResolutionsRefClipMismatchError',

    'InvalidVideoFormatError',
    'InvalidColorFamilyError',
    'InvalidSubsamplingError',

    'UnsupportedVideoFormatError',
    'UnsupportedColorFamilyError',
    'UnsupportedSubsamplingError',

    'FramePropError',

    'TopFieldFirstError',

    'InvalidFramerateError'
]


class FramesLengthError(CustomOverflowError):
    def __init__(
        self, func: FuncExceptT,
        var_name: str, message: SupportsString = '"{var_name}" can\'t be greater than the clip length!',
        **kwargs: Any
    ) -> None:
        super().__init__(message, func, var_name=var_name, **kwargs)


class ClipLengthError(CustomOverflowError):
    ...


class VariableFormatError(CustomValueError):
    """Raised when clip is of a variable format."""

    def __init__(
        self, func: FuncExceptT, message: SupportsString = 'Variable-format clips not supported!',
        **kwargs: Any
    ) -> None:
        super().__init__(message, func, **kwargs)


class VariableResolutionError(CustomValueError):
    """Raised when clip is of a variable resolution."""

    def __init__(
        self, func: FuncExceptT, message: SupportsString = 'Variable-resolution clips not supported!',
        **kwargs: Any
    ) -> None:
        super().__init__(message, func, **kwargs)


class UnsupportedVideoFormatError(CustomValueError):
    """Raised when an undefined video format value is passed."""


class InvalidVideoFormatError(CustomValueError):
    """Raised when the given clip has an invalid format."""

    def __init__(
        self, func: FuncExceptT, format: VideoFormatT | HoldsVideoFormatT,
        message: SupportsString = 'The format {format.name} is not supported!',
        **kwargs: Any
    ) -> None:
        from ..utils import get_video_format
        super().__init__(message, func, format=get_video_format(format), **kwargs)


class UnsupportedColorFamilyError(CustomValueError):
    """Raised when an undefined color family value is passed."""


class InvalidColorFamilyError(CustomValueError):
    """Raised when the given clip uses an invalid format."""

    def __init__(
        self, func: FuncExceptT | None,
        wrong: VideoFormatT | HoldsVideoFormatT | vs.ColorFamily,
        correct: VideoFormatT | HoldsVideoFormatT | vs.ColorFamily | Iterable[
            VideoFormatT | HoldsVideoFormatT | vs.ColorFamily
        ] = vs.YUV,
        message: SupportsString = 'Input clip must be of {correct} color family, not {wrong}!',
        **kwargs: Any
    ) -> None:
        from ..functions import to_arr
        from ..utils import get_color_family

        wrong_str = get_color_family(wrong).name

        super().__init__(
            message, func, wrong=wrong_str,
            correct=iter(set(get_color_family(c).name for c in to_arr(correct))), **kwargs  # type: ignore[arg-type]
        )

    @staticmethod
    def check(
        to_check: VideoFormatT | HoldsVideoFormatT | vs.ColorFamily,
        correct: VideoFormatT | HoldsVideoFormatT | vs.ColorFamily | Iterable[
            VideoFormatT | HoldsVideoFormatT | vs.ColorFamily
        ],
        func: FuncExceptT | None = None, message: SupportsString | None = None,
        **kwargs: Any
    ) -> None:
        from ..functions import to_arr
        from ..utils import get_color_family
        to_check = get_color_family(to_check)
        correct_list = [get_color_family(c) for c in to_arr(correct)]  # type: ignore

        if to_check not in correct_list:
            if message is not None:
                kwargs.update(message=message)
            raise InvalidColorFamilyError(func, to_check, correct_list, **kwargs)


class UnsupportedSubsamplingError(CustomValueError):
    """Raised when an undefined subsampling value is passed."""


class InvalidSubsamplingError(CustomValueError):
    """Raised when the given clip has invalid subsampling."""

    def __init__(
        self, func: FuncExceptT, subsampling: str | VideoFormatT | HoldsVideoFormatT,
        message: SupportsString = 'The subsampling {subsampling} is not supported!',
        **kwargs: Any
    ) -> None:
        from ..utils import get_video_format
        subsampling = subsampling if isinstance(subsampling, str) else get_video_format(subsampling).name
        super().__init__(message, func, subsampling=subsampling, **kwargs)


class FormatsMismatchError(CustomValueError):
    """Raised when clips with different formats are given."""

    def __init__(
        self, func: FuncExceptT, message: SupportsString = 'The format of both clips must be equal!',
        **kwargs: Any
    ) -> None:
        super().__init__(message, func, **kwargs)


class FormatsRefClipMismatchError(FormatsMismatchError):
    """Raised when a ref clip and the main clip have different formats"""

    def __init__(
        self, func: FuncExceptT, message: SupportsString = 'The format of ref and main clip must be equal!',
        **kwargs: Any
    ) -> None:
        super().__init__(func, message, **kwargs)


class ResolutionsMismatchError(CustomValueError):
    """Raised when clips with different resolutions are given."""

    def __init__(
        self, func: FuncExceptT, message: SupportsString = 'The resolution of both clips must be equal!',
        **kwargs: Any
    ) -> None:
        super().__init__(message, func, **kwargs)


class ResolutionsRefClipMismatchError(ResolutionsMismatchError):
    """Raised when a ref clip and the main clip have different resolutions"""

    def __init__(
        self, func: FuncExceptT, message: SupportsString = 'The resolution of ref and main clip must be equal!',
        **kwargs: Any
    ) -> None:
        super().__init__(func, message, **kwargs)


class FramePropError(CustomKeyError):
    """Raised when there is an error with the frame props."""

    def __init__(
        self, func: FuncExceptT, key: str, message: SupportsString = 'Error while trying to get frame prop "{key}"!',
        **kwargs: Any
    ) -> None:
        super().__init__(message, func, key=key, **kwargs)


class TopFieldFirstError(CustomValueError):
    """Raised when the user must pass a TFF argument."""

    def __init__(
        self, func: FuncExceptT, message: SupportsString = 'You must set `tff` for this clip!',
        **kwargs: Any
    ) -> None:
        super().__init__(message, func, **kwargs)


class InvalidFramerateError(CustomValueError):
    """Raised when the given clip has an invalid framerate."""

    def __init__(self, func: FuncExceptT, clip: vs.VideoNode | Fraction,
                 message: SupportsString = '{fps} clips are not allowed!', **kwargs: Any) -> None:
        super().__init__(
            message, func, fps=clip.fps if isinstance(clip, vs.VideoNode) else clip, **kwargs  # type: ignore
        )

    @staticmethod
    def check(
        func: FuncExceptT, to_check: vs.VideoNode | Fraction | tuple[int, int] | float,
        correct: vs.VideoNode | Fraction | tuple[int, int] | float | Iterable[
            vs.VideoNode | Fraction | tuple[int, int] | float
        ], message: SupportsString = 'Input clip must have {correct} framerate, not {wrong}!', **kwargs: Any
    ) -> None:
        from ..functions import to_arr
        from ..utils import get_framerate

        to_check = get_framerate(to_check)
        correct_list = [
            get_framerate(c) for c in ([correct] if isinstance(correct, tuple) else to_arr(correct))  # type: ignore
        ]

        if to_check not in correct_list:
            raise InvalidFramerateError(
                func, to_check, message, wrong=to_check, correct=iter(set(correct_list)), **kwargs
            )
