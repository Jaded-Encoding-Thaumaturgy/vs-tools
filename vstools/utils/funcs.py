from __future__ import annotations
from typing import Sequence

from stgpytools import copy_func, erase_module as stg_erase_module, F

__all__ = [
    'copy_func',
    'erase_module'
]


def erase_module(func: F, modules: Sequence[str] | None = None, *, vs_only: bool = False) -> F:
    """Delete the __module__ of the function."""

    return stg_erase_module(func, ['__vapoursynth__', *(modules or [])] if vs_only else modules)
