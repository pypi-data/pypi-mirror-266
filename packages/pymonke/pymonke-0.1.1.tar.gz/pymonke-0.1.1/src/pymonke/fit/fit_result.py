import pandas as pd
from mypy_extensions import VarArg
import numpy as np
from numpy.typing import NDArray
from uncertainties import ufloat
from uncertainties.core import Variable, AffineScalarFunc

from dataclasses import dataclass, field
from typing import List, Dict, Callable, TypeAlias, Iterable, Any, Optional, Tuple, Type

scalar: TypeAlias = int | float
array: TypeAlias = np.ndarray | pd.Series
numerical: TypeAlias = scalar | array
measurement: TypeAlias = Variable | AffineScalarFunc
func_type: TypeAlias = Callable[[numerical, VarArg(scalar)], numerical]


@dataclass(repr=True)
class FitResult:
    function: func_type = field(repr=False)
    parameter_names: List[str]
    # parameter_values: np.ndarray
    # parameter_sigmas: np.ndarray
    parameter_measurements: NDArray[measurement]
    reduced_chi_squared: float | None = field(default=None)
    residual_variance: float | None = field(default=None)

    @property
    def parameter_values(self) -> np.ndarray:
        return np.array([i.nominal_value for i in self.parameter_measurements])

    @property
    def parameter_sigmas(self) -> np.ndarray:
        return np.array([i.std_dev for i in self.parameter_measurements])

    def eval(self, x: numerical) -> float | np.ndarray:
        """Calculated values of the fitted function"""
        result = self.function(x, *self.parameter_values)
        if isinstance(result, Iterable):
            return np.array(result)
        else:
            return float(result)

    def as_dict(self, chi_square: bool = True) -> dict[str, Any | float]:
        result_: dict = dict()
        for name, x in zip(self.parameter_names, self.parameter_measurements):
            result_[name] = x

        if chi_square:
            result_["reduced_chi_squared"] = self.reduced_chi_squared

        return result_

    def __getitem__(self, item: str) -> Variable | AffineScalarFunc:
        index: int = -1
        for i, name in enumerate(self.parameter_names):
            if name == item:
                index = i
        if index == -1:
            text = f"parameter name {item} not found."
            raise KeyError(text)

        return self.parameter_measurements[index]  # type: ignore

    def set_reduced_chi_squared(self, x: array, y: array, sigma: array) -> float:
        chi_squared = ((self.eval(x) - y) ** 2 / sigma ** 2).sum()
        result: float = chi_squared / (len(x) - len(self.parameter_names))
        self.reduced_chi_squared = result
        return result


def result(function: func_type, x: array, y: array, sy: array, *,
           param_names: list[str], params: Iterable[float | measurement],
           params_std_dev: Optional[array] = None, sx: Optional[Iterable[float]] = None) -> FitResult:
    """creates a FitResult object with proper goodness of fit."""
    param_data: NDArray[measurement]
    if iterable_is_type(params, (Variable, AffineScalarFunc)):
        param_data = np.array(params)  # type: ignore
    elif iterable_is_type(params, float):
        assert params_std_dev is not None
        param_data = np.array([ufloat(x, err) for x, err in zip(params, params_std_dev)])  # type: ignore
    else:
        raise ValueError("parameters arguments must be either an iterable of floats or of numbers with uncertainties.")

    fit_result = FitResult(function, param_names, param_data)
    fit_result.set_reduced_chi_squared(x, y, sy)

    return fit_result


def iterable_is_type(iterable: Iterable[Any], t: type | tuple) -> bool:
    for i in iterable:
        if not isinstance(i, t):
            return False

    return True
