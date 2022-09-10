from __future__ import annotations

import vapoursynth as vs

from ..types import F
from .base import CustomKeyError, CustomValueError

__all__ = [
    'VariableFormatError', 'VariableResolutionError',

    'FormatsMismatchError', 'FormatsRefClipMismatchError',

    'ResolutionsMismatchError', 'ResolutionsRefClipMismatchError',

    'InvalidVideoFormatError', 'InvalidColorFamilyError',

    'FramePropError',

    'TopFieldFirstError',

    'InvalidFramerateError'
]


class VariableFormatError(CustomValueError):
    """Raised when clip is of a variable format."""

    def __init__(self, function: str | F, message: str = 'Variable-format clips not supported!') -> None:
        super().__init__(message, function)


class VariableResolutionError(CustomValueError):
    """Raised when clip is of a variable resolution."""

    def __init__(self, function: str | F, message: str = 'Variable-resolution clips not supported!') -> None:
        super().__init__(message, function)


class InvalidVideoFormatError(CustomValueError):
    """Raised when the given clip has an invalid format."""

    def __init__(
        self, function: str | F, format: vs.VideoNode | vs.VideoFrame | vs.VideoFormat,
        message: str = 'The format {format.name} is not supported!'
    ) -> None:
        from ..utils import get_format
        super().__init__(message, function, format=get_format(format))


class InvalidColorFamilyError(CustomValueError):
    """Raised when the given clip uses an invalid format."""

    def __init__(
        self, function: str | F,
        wrong: vs.ColorFamily | vs.VideoFormat,
        correct: vs.ColorFamily | list[vs.ColorFamily] | vs.VideoFormat | list[vs.VideoFormat] = vs.YUV,
        message: str = 'Input clip must be of {correct} color family, not {wrong}!'
    ) -> None:
        wrong_str = (wrong if isinstance(wrong, vs.ColorFamily) else wrong.color_family).name

        correct_str = ', '.join(
            list(set([
                (c if isinstance(c, vs.ColorFamily) else c.color_family).name
                for c in (correct if isinstance(correct, list) else [correct])
            ]))
        )

        super().__init__(message, function, wrong=wrong_str, correct=correct_str)


class FormatsMismatchError(CustomValueError):
    """Raised when clips with different formats are given."""

    def __init__(self, function: str | F, message: str = 'The format of both clips must be equal!') -> None:
        super().__init__(message, function)


class FormatsRefClipMismatchError(FormatsMismatchError):
    """Raised when a ref clip and the main clip have different formats"""

    def __init__(
        self, function: str | F, message: str = 'The format of ref and main clip must be equal!'
    ) -> None:
        super().__init__(function, message)


class ResolutionsMismatchError(CustomValueError):
    """Raised when clips with different resolutions are given."""

    def __init__(
        self, function: str | F, message: str = 'The resolution of both clips must be equal!'
    ) -> None:
        super().__init__(message, function)


class ResolutionsRefClipMismatchError(ResolutionsMismatchError):
    """Raised when a ref clip and the main clip have different resolutions"""

    def __init__(
        self, function: str | F, message: str = 'The resolution of ref and main clip must be equal!'
    ) -> None:
        super().__init__(function, message)


class FramePropError(CustomKeyError):
    """Raised when there is an error with the frame props."""

    def __init__(
        self, function: str | F, key: str, message: str = 'Error while trying to get frame prop "{key}"!'
    ) -> None:
        super().__init__(message, function, key=key)


class TopFieldFirstError(CustomValueError):
    """Raised when the user must pass a TFF argument."""

    def __init__(
        self, function: str | F, message: str = 'You must set `tff` for this clip!'
    ) -> None:
        super().__init__(message, function)


class InvalidFramerateError(CustomValueError):
    """Raised when the given clip has an invalid framerate."""

    def __init__(
        self, function: str | F, clip: vs.VideoNode, message: str = '{fps} clips are not allowed!'
    ) -> None:
        super().__init__(message, function, fps=clip.fps)
