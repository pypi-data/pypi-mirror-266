from typing import List, TypeAlias

import math
import numpy as np
from pandas import Series

scalar: TypeAlias = float | int
array: TypeAlias = np.ndarray | Series
numeric: TypeAlias = scalar | array


def roundup(x: numeric, r: int = 2) -> numeric:
    a: numeric = x * 10 ** r
    a = np.ceil(a)
    a = a * 10 ** (-r)

    return np.around(a, r)


def roundup_two_significant_digits(x: float) -> float:
    """Rounds the given number up to 2 significant digits"""
    scientific: List[str] = "{:e}".format(x).split("e")
    value, exponent = float(scientific[0]), int(scientific[1])
    if value < 2:
        value = roundup(value, 1)
    else:
        value = roundup(value, 0)

    return float(f"{value}e{exponent}")



