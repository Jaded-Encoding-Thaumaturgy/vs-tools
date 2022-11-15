from __future__ import annotations

from functools import partial
from typing import Sequence
from math import ceil, log

from ..types import Nb

__all__ = [
    'clamp', 'clamp_arr',

    'cround',

    'mod_x', 'mod2', 'mod4', 'mod8',

    'next_power_of_x', 'next_power_of_2'
]


def clamp(val: Nb, min_val: Nb, max_val: Nb) -> Nb:
    return min_val if val < min_val else max_val if val > max_val else val


def clamp_arr(vals: Sequence[Nb], min_val: Nb, max_val: Nb) -> list[Nb]:
    return [clamp(x, min_val, max_val) for x in vals]


def cround(x: float, *, eps: float = 1e-6) -> int:
    return round(x + (eps if x > 0. else - eps))


def mod_x(val: int | float, x: int) -> int:
    return max(x * x, cround(val / x) * x)


mod2 = partial(mod_x, x=2)

mod4 = partial(mod_x, x=4)

mod8 = partial(mod_x, x=8)


def next_power_of_2(x: float) -> int:
    x = cround(x)

    if x == 0:
        return 1

    if x & (x - 1) == 0:
        return x

    while x & (x - 1) > 0:
        x &= (x - 1)

    return x << 1


def next_power_of_y(x: float, y: int) -> int:
    return 1 if x == 0 else y ** ceil(log(x, y))
