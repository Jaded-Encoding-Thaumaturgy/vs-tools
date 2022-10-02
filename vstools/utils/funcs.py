from __future__ import annotations

from functools import update_wrapper
from types import FunctionType

from ..types import F

__all__ = [
    'copy_func',
    'erase_module'
]


def copy_func(f: F) -> FunctionType:
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
    if hasattr(func, '__module__') and (
        func.__module__ == '__vapoursynth__' if vs_only else True
    ):
        func.__module__ = None  # type: ignore

    return func
