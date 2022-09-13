from __future__ import annotations

from typing import Any, Iterable

import vapoursynth as vs

from ..types import FuncExceptT, HoldsVideoFormatT
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
        self, function: FuncExceptT,
        var_name: str, message: str = '"{var_name}" can\'t be greater than the clip length!',
        **kwargs: Any
    ) -> None:
        """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
        super().__init__(message, function, var_name=var_name, **kwargs)


class ClipLengthError(CustomOverflowError):
    ...


class VariableFormatError(CustomValueError):
    """Raised when clip is of a variable format."""

    def __init__(
        self, function: FuncExceptT, message: str = 'Variable-format clips not supported!',
        **kwargs: Any
    ) -> None:
        """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
        super().__init__(message, function, **kwargs)


class VariableResolutionError(CustomValueError):
    """Raised when clip is of a variable resolution."""

    def __init__(
        self, function: FuncExceptT, message: str = 'Variable-resolution clips not supported!',
        **kwargs: Any
    ) -> None:
        """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
        super().__init__(message, function, **kwargs)


class UnsupportedVideoFormatError(CustomValueError):
    """Raised when an undefined video format value is passed."""


class InvalidVideoFormatError(CustomValueError):
    """Raised when the given clip has an invalid format."""

    def __init__(
        self, function: FuncExceptT, format: HoldsVideoFormatT,
        message: str = 'The format {format.name} is not supported!',
        **kwargs: Any
    ) -> None:
        """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
        from ..utils import get_format
        super().__init__(message, function, format=get_format(format), **kwargs)


class UnsupportedColorFamilyError(CustomValueError):
    """Raised when an undefined color family value is passed."""


class InvalidColorFamilyError(CustomValueError):
    """Raised when the given clip uses an invalid format."""

    def __init__(
        self, function: FuncExceptT | None,
        wrong: HoldsVideoFormatT | vs.ColorFamily,
        correct: HoldsVideoFormatT | vs.ColorFamily | Iterable[HoldsVideoFormatT | vs.ColorFamily] = vs.YUV,
        message: str = 'Input clip must be of {correct} color family, not {wrong}!',
        **kwargs: Any
    ) -> None:
        """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
        from ..functions import to_arr
        from ..utils import get_color_family
        wrong_str = get_color_family(wrong).name
        correct_str = ', '.join(set(get_color_family(c).name for c in to_arr(correct)))  # type: ignore
        super().__init__(message, function, wrong=wrong_str, correct=correct_str, **kwargs)

    @staticmethod
    def check(
        to_check: HoldsVideoFormatT | vs.ColorFamily,
        correct: HoldsVideoFormatT | vs.ColorFamily | Iterable[HoldsVideoFormatT | vs.ColorFamily],
        func: FuncExceptT | None = None, message: str | None = None,
        **kwargs: Any
    ) -> None:
        """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
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
        self, function: FuncExceptT, subsampling: str | HoldsVideoFormatT,
        message: str = 'The subsampling {subsampling} is not supported!',
        **kwargs: Any
    ) -> None:
        """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
        from ..utils import get_format
        subsampling = subsampling if isinstance(subsampling, str) else get_format(subsampling).name
        super().__init__(message, function, subsampling=subsampling, **kwargs)


class FormatsMismatchError(CustomValueError):
    """Raised when clips with different formats are given."""

    def __init__(
        self, function: FuncExceptT, message: str = 'The format of both clips must be equal!',
        **kwargs: Any
    ) -> None:
        """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
        super().__init__(message, function, **kwargs)


class FormatsRefClipMismatchError(FormatsMismatchError):
    """Raised when a ref clip and the main clip have different formats"""

    def __init__(
        self, function: FuncExceptT, message: str = 'The format of ref and main clip must be equal!',
        **kwargs: Any
    ) -> None:
        """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
        super().__init__(function, message, **kwargs)


class ResolutionsMismatchError(CustomValueError):
    """Raised when clips with different resolutions are given."""

    def __init__(
        self, function: FuncExceptT, message: str = 'The resolution of both clips must be equal!',
        **kwargs: Any
    ) -> None:
        """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
        super().__init__(message, function, **kwargs)


class ResolutionsRefClipMismatchError(ResolutionsMismatchError):
    """Raised when a ref clip and the main clip have different resolutions"""

    def __init__(
        self, function: FuncExceptT, message: str = 'The resolution of ref and main clip must be equal!',
        **kwargs: Any
    ) -> None:
        """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
        super().__init__(function, message, **kwargs)


class FramePropError(CustomKeyError):
    """Raised when there is an error with the frame props."""

    def __init__(
        self, function: FuncExceptT, key: str, message: str = 'Error while trying to get frame prop "{key}"!',
        **kwargs: Any
    ) -> None:
        """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
        super().__init__(message, function, key=key, **kwargs)


class TopFieldFirstError(CustomValueError):
    """Raised when the user must pass a TFF argument."""

    def __init__(
        self, function: FuncExceptT, message: str = 'You must set `tff` for this clip!',
        **kwargs: Any
    ) -> None:
        """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
        super().__init__(message, function, **kwargs)


class InvalidFramerateError(CustomValueError):
    """Raised when the given clip has an invalid framerate."""

    def __init__(
        self, function: FuncExceptT, clip: vs.VideoNode, message: str = '{fps} clips are not allowed!',
        **kwargs: Any
    ) -> None:
        """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
        super().__init__(message, function, fps=clip.fps, **kwargs)
