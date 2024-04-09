from colorama import Fore, Style
import timeit
from typing import Any, TypeAlias, Callable

import numpy as np

from ..mmath.rounding import roundup

func: TypeAlias = Callable[[], Any]


def green(text: str) -> str:
    return f"{Fore.GREEN} {text} {Style.RESET_ALL}"


def red(text: str) -> str:
    return f"{Fore.RED}{text}{Style.RESET_ALL}"


def bench_compare(func1: func, func2: func, name: str, number: int = 10_000, iters: int = 20) -> None:
    x1: Any = []
    x2: Any = []
    for _ in range(iters):
        x1.append(timeit.timeit(func1, globals=locals(), number=number) / number)
        x2.append(timeit.timeit(func2, globals=locals(), number=number) / number)
    x1, x2 = np.array(x1[1:]), np.array(x2[1:])
    m1, m2 = x1.mean(), x2.mean()
    std1, std2 = x1.std(), x2.std()
    if m1 > m2:
        x = round(m1 / m2 - 1, 2)
        err = roundup(np.sqrt((std1 / m2)**2 + (m1*std2 / m2**2)**2), 2)
        print(f"{name} benchmark: {x}x +- {err}x {green('faster')} {iters * number} iterations.")
    else:
        x = round(m2 / m1 - 1, 2)
        err = roundup(np.sqrt((std2 / m1) ** 2 + (m2 * std1 / m1 ** 2) ** 2), 2)
        print(f"{name} benchmark: {x}x +- {err}x {red('slower')} {iters * number} iterations.")


def timing(number: int = 10_000, iters: int = 20) -> Callable:
    def _timing(_func: Callable) -> Callable:
        def inner():
            runs = []
            for _ in range(iters):
                runs.append(timeit.timeit(_func, globals=locals(), number=number) / number)
            mean, std = np.mean(runs[1:]), np.std(runs[1:])

            x, err = "{:.2e}".format(mean), "{:.2e}".format(std)
            print(f"Function '{_func.__name__}' benchmark: {x} +- {err} seconds with {iters * number} iterations.")

        return inner

    return _timing
