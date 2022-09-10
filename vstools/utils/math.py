from __future__ import annotations

from ..types import Nb

__all__ = [
    'clamp',

    'cround',

    'mod_x', 'mod2', 'mod4', 'mod8'
]


def clamp(val: Nb, min_val: Nb, max_val: Nb) -> Nb:
    """Faster max(min(value, max_val), min_val) "wrapper" """
    return min_val if val < min_val else max_val if val > max_val else val


def cround(x: float, *, eps: float = 1e-6) -> int:
    """Rounding function that accounts for float's imprecision."""
    return round(x + (eps if x > 0. else - eps))


def mod_x(val: int | float, x: int) -> int:
    """Force a value to be divisible by x (val % x == 0)."""
    return max(x * x, cround(val / x) * x)


def mod2(val: int | float) -> int:
    """Force a value to be mod 2"""
    return mod_x(val, x=2)


def mod4(val: int | float) -> int:
    """Force a value to be mod 4"""
    return mod_x(val, x=4)


def mod8(val: int | float) -> int:
    """Force a value to be mod 8"""
    return mod_x(val, x=8)
