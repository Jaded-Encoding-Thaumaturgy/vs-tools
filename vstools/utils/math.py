from __future__ import annotations

from functools import partial
from math import ceil, log
from typing import Sequence

from ..types import Nb

__all__ = [
    'clamp', 'clamp_arr',

    'cround',

    'mod_x', 'mod2', 'mod4', 'mod8',

    'next_power_of_y', 'next_power_of_2',

    'spline_coeff'
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
    if x == 0:
        return 1

    return int(y ** ceil(log(x, y)))


def spline_coeff(
    x: int, coordinates: list[tuple[float, float]] = [
        (0, 0), (0.5, 0.1), (1, 0.6), (2, 0.9), (2.5, 1), (3, 1.1), (3.5, 1.15), (4, 1.2), (8, 1.25), (255, 1.5)
    ]
) -> float:
    length = len(coordinates)

    if length < 3:
        raise ValueError("coordinates require at least three pairs")

    px, py = zip(*coordinates)

    matrix = [[1.0] + [0.0] * length]

    for i in range(1, length - 1):
        p = [0.0] * (length + 1)

        p[i - 1] = px[i] - px[i - 1]
        p[i] = 2 * (px[i + 1] - px[i - 1])
        p[i + 1] = px[i + 1] - px[i]
        p[length] = 6 * (((py[i + 1] - py[i]) / p[i + 1]) - (py[i] - py[i - 1]) / p[i - 1])

        matrix.append(p)

    matrix += [([0.0] * (length - 1) + [1.0, 0.0])]

    for i in range(length):
        num = matrix[i][i]

        for j in range(length + 1):
            matrix[i][j] /= num

        for j in range(length):
            if i != j:
                a = matrix[j][i]

                for k in range(i, length + 1):
                    matrix[j][k] -= a * matrix[i][k]

    for i in range(length + 1):
        if x >= px[i] and x <= px[i + 1]:
            break

    j = i + 1

    h = px[j] - px[i]

    s = matrix[j][length] * float((x - px[i]) ** 3)
    s -= matrix[i][length] * float((x - px[j]) ** 3)

    s /= 6 * h

    s += (py[j] / h - h * matrix[j][length] / 6) * (x - px[i])
    s -= (py[i] / h - h * matrix[i][length] / 6) * (x - px[j])

    return s
