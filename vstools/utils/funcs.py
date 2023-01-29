from __future__ import annotations

import inspect
from functools import update_wrapper
from pathlib import Path
from types import FunctionType

from ..types import F

__all__ = [
    'copy_func',
    'erase_module',
    'get_caller_name'
]


def copy_func(f: F) -> FunctionType:
    """Try copying a function."""

    try:
        g = FunctionType(
            f.__code__, f.__globals__, name=f.__name__, argdefs=f.__defaults__, closure=f.__closure__
        )
        g = update_wrapper(g, f)
        g.__kwdefaults__ = f.__kwdefaults__
        return g
    except BaseException:  # for builtins
        return f  # type: ignore


def erase_module(func: F, *, vs_only: bool = False) -> F:
    """Delete the __module__ of the function."""

    if hasattr(func, '__module__') and (
        func.__module__ == '__vapoursynth__' if vs_only else True
    ):
        func.__module__ = None  # type: ignore

    return func


def get_caller_function() -> str | None:
    """Attempt to call the caller function."""
    for f in inspect.stack()[1:]:
        func = f.function

        # Check if private function/method
        if func.startswith("_"):
            continue

        # TODO: Combine the following two checks into one somehow?
        # Check if it's an exception or error class.
        if any(x in func for x in ["Exceptions", "Errors"]):
            continue

        # Check if it originates from an `exceptions.py` or `errors.py` file.
        if any(x in Path(f.filename).name.lower() for x in ["exception", "error"]):
            continue

        # TODO: Check for class method. If method, return `ClassName.method`.

        # Finally, return the function name.
        return func

    return None
