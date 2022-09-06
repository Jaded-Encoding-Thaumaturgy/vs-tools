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
    return min_val if val < min_val else max_val if val > max_val else val


def cround(x: float) -> int:
    return floor(x + 0.5) if x > 0 else ceil(x - 0.5)


def mod_x(val: int | float, x: int) -> int:
    return max(x * x, cround(val / x) * x)


mod2 = partial(mod_x, x=2)

mod4 = partial(mod_x, x=4)

mod8 = partial(mod_x, x=8)
