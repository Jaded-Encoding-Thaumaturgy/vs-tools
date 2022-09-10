from __future__ import annotations

from functools import partial
from math import ceil, floor

from ..types import Nb

__all__ = [
    'clamp',

    'cround',

    'mod_x', 'mod2', 'mod4'
]


def clamp(val: Nb, min_val: Nb, max_val: Nb) -> Nb:
    """Wrapper around min/max."""
    return min_val if val < min_val else max_val if val > max_val else val


def cround(x: float, *, eps: float = 1e-6) -> int:
    """Rounding function that accounts for imprecise float calculations."""
    return round(x + (eps if x > 0. else - eps))


def mod_x(val: int | float, x: int) -> int:
    """Force a value to comply to MOD# values."""
    return max(x * x, cround(val / x) * x)


mod2 = partial(mod_x, x=2)

mod4 = partial(mod_x, x=4)

mod8 = partial(mod_x, x=8)
