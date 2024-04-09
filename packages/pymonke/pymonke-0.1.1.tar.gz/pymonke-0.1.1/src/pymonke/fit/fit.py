from typing import List, Dict, Tuple, Callable, TypeAlias, Optional, Any
import warnings

import matplotlib.pyplot as plt
from matplotlib.figure import Figure, SubFigure
from matplotlib.axes import Axes
from mypy_extensions import VarArg
import numpy as np
from pandas import DataFrame, Series
from scipy import odr
from scipy.optimize import curve_fit

from .fit_result import FitResult, result
from .parse import parse_function, replace_funcs, numerical, scalar, array, parse_variable_str
from ..misc.dataframe import get_error_column_name, has_uncertainty
from ..misc.file_management import read_data_into_dataframe

func_type: TypeAlias = Callable[[numerical, VarArg(scalar)], numerical]


class Fit:
    def __init__(self, meta: dict, data: DataFrame | None = None):
        self.meta = meta
        if data is None:
            self.file: str = meta["file"]
            if (args := meta.get("read_data_args")) is not None:
                self.data: DataFrame = read_data_into_dataframe(self.file, **args)
            else:
                self.data = read_data_into_dataframe(self.file)
        else:
            self.data = data

        self.result: Optional[dict[str, FitResult]] = None

        self.column_names = self.__get_column_names(meta.get("error_marker"))

    def __get_column_names(self, error_marker: List[str] | None = None) -> Dict[str, str]:
        if error_marker is None:
            error_marker = ["err", "error", "fehler", "Err", "Error", "Fehler"]
        names: Dict[str, str] = dict()
        names["x"] = self.meta["x"]
        names["y"] = self.meta["y"]
        x_error = get_error_column_name(self.data, names["x"], error_marker)
        y_error = get_error_column_name(self.data, names["y"], error_marker)

        names["y error"] = y_error
        names["x error"] = x_error

        return names

    # ------------------------------------------------------------------------------------
    # -------------------------------Plot with Matplotlib---------------------------------
    # ------------------------------------------------------------------------------------
    def plot(self, figure_id: Optional[int | str | Figure | SubFigure] = None, ax: Optional[Axes] = None):
        if (style := self.meta.get("figure_style")) is None:
            style = "science"
        try:
            plt.style.use(style)
        except Exception as e:
            message = f"figure style {style} not found. Using default instead.\n{e}"
            warnings.warn(message, RuntimeWarning)
            plt.style.use("default")

        if ax is None:
            if (size := self.meta.get("figure_size")) is None:
                size = (6, 4.7)
            if (dpi := self.meta.get("figure_dpi")) is None:
                dpi = 120
            plt.figure(num=figure_id, figsize=size, dpi=dpi)

        data = self.__get_data()
        x, y, sx, sy = data["x"], data["y"], data["sx"], data["sy"]

        plotting_style = {
            "linestyle": "",
            "ms": 4,
            "marker": "o",
            "capsize": 3.5,
            "zorder": 2
        }

        if (more_style := self.meta.get("plotting_style")) is not None:
            plotting_style.update(more_style)

        if ax is None:
            plt.errorbar(x, y, yerr=sy, xerr=sx, **plotting_style,
                         label=self.meta.get("label") or "Data Points")
            plt.xlim(self.__get_xlim(self.meta))
            plt.ylim(self.__get_ylim(self.meta, plt.ylim()))
            plt.rc('axes', axisbelow=True)
        else:
            ax.errorbar(x, y, yerr=sy, xerr=sx, **plotting_style,
                        label=self.meta.get("label") or "Data Points")
            ax.set_xlim(self.__get_xlim(self.meta))
            ax.set_ylim(self.__get_ylim(self.meta, ax.get_ylim()))
            ax.set_axisbelow(True)

        if self.result is not None:
            for fit_name in self.result.keys():
                self.__plot_fit(fit_name, self.result[fit_name], ax)

        if ax is None:
            plt.legend()
        else:
            ax.legend()

    def __plot_fit(self, name: str, fit_res: FitResult, ax: Optional[Axes] = None) -> None:
        meta: dict = self.meta["fits"][name]
        if (points := meta.get("fit_points")) is None:
            points = 150

        plotting_style = {
            "linestyle": "--",
            "zorder": 1,
            "linewidth": 1.6,
        }

        if (more_style := meta.get("plotting_style")) is not None:
            plotting_style.update(more_style)

        limits: List[float] = list(self.__get_xlim(meta))
        if (val := meta.get("plot_x_min_limit")) is not None:
            limits[0] = val
        if (val := meta.get("plot_x_max_limit")) is not None:
            limits[1] = val
        x = np.linspace(*limits, points)
        label = parse_variable_str(meta.get("label") or "$\\chi^2 = #chi $", fit_res, self.meta.get("latex") or False)
        if ax is None:
            plt.plot(x, fit_res.eval(x), **plotting_style, label=label)
        else:
            ax.plot(x, fit_res.eval(x), **plotting_style, label=label)

    # ----------------------------------------------------------------------------------------

    def get_results_as_dict(self) -> Dict[str, Any]:
        result = dict()
        for key, value in self.result.items():
            result[key] = value.as_dict(True)

        return result

    def __get_xlim(self, meta: dict) -> Tuple[float, float]:
        x = self.column_names["x"]
        if (x_min := meta.get("x_min_limit")) is None:
            x_min = self.data[x].min()
        if (x_max := meta.get("x_max_limit")) is None:
            x_max = self.data[x].max()

        return x_min, x_max

    def __get_ylim(self, meta: dict, ylim: Tuple[float, float]) -> Tuple[float, float]:
        ylim = list(ylim)
        if (y_min := meta.get("y_min_limit")) is not None:
            ylim[0] = y_min
        if (y_max := meta.get("y_max_limit")) is not None:
            ylim[1] = y_max

        return tuple(ylim)

    def run(self) -> dict[str, FitResult]:
        if (val := self.meta.get("fits")) is None:
            return dict()
        fits_meta: dict[str, dict] = val
        result: dict[str, FitResult] = dict()
        for fit_name in fits_meta.keys():
            result[fit_name] = self.__do_fit(fits_meta[fit_name])

        self.result = result

        return result

    def __do_fit(self, meta: dict) -> FitResult:
        if meta["fit_type"] == "optimize.curve_fit":
            return self.__do_optimize_curve_fit(meta)
        elif meta["fit_type"] == "odr":
            return self.__do_odr_fit(meta)
        else:
            raise ValueError(f"unknown fit type: {meta['fit_type']}")

    def __do_optimize_curve_fit(self, meta: dict) -> FitResult:
        function, params, p0, lim, arrays = self.__get_fitting_data(meta)
        x, y, y_error = arrays["x"], arrays["y"], arrays["sy"]
        assert isinstance(x, Series) and isinstance(y, Series) and isinstance(y_error, Series)

        if (b := meta.get("absolute_sigma")) is None:
            b = False
        if (check_finite := meta.get("check_finite")) is None:
            check_finite = False
        out: tuple = curve_fit(function, xdata=x, ydata=y, sigma=y_error, absolute_sigma=b,
                               check_finite=check_finite, p0=p0)
        popt, pcov = out
        # fit_res = FitResult(function, params, popt, np.sqrt(pcov.diagonal()))
        # fit_res.set_reduced_chi_squared(x, y, y_error)
        fit_res = result(function, x, y, y_error, param_names=params, params=popt,
                         params_std_dev=np.sqrt(pcov.diagonal()))
        return fit_res

    def __do_odr_fit(self, meta: dict) -> FitResult:
        function, params, p0, lim, arrays = self.__get_fitting_data(meta)
        x, y, sy = arrays["x"], arrays["y"], arrays["sy"]
        sx = arrays.get("sx")
        assert isinstance(x, Series) and isinstance(y, Series) and isinstance(sy, Series)
        if (b := meta.get("absolute_sigma")) is None:
            b = False

        if b:
            odr_data = odr.RealData(x=x, y=y, sy=sy, sx=sx)
        else:
            wd = None
            if sx is not None:
                wd = 1 / sx ** 2
            odr_data = odr.Data(x=x, y=y, we=1 / sy ** 2, wd=wd)

        def odr_func(_b: list, _x: float | int) -> numerical:
            return function(_x, *_b)

        odr_model = odr.Model(odr_func)
        odr_odr = odr.ODR(odr_data, odr_model, p0)
        odr_out: odr.Output = odr_odr.run()
        # fit_res = FitResult(function, params, odr_out.beta, odr_out.sd_beta)
        # fit_res.set_reduced_chi_squared(x, y, sy)
        fit_res = result(function, x, y, sy, param_names=params, params=odr_out.beta, params_std_dev=odr_out.sd_beta,
                         sx=sx)
        return fit_res

    def __get_fitting_data(self, meta: dict) -> Any:

        p0: List[float | int] = meta["start_parameters"]
        x_min, x_max = self.__get_xlim(meta)

        query = f"{self.column_names['x']} >= {x_min} and {self.column_names['x']} <= {x_max}"
        # data = self.data.query(query)

        fitting_data = self.__get_data(query)

        function, params = parse_function(replace_funcs(meta["function"]))

        lim: Tuple[float, float] = (x_min, x_max)

        return function, params, p0, lim, fitting_data

    def __get_data(self, query: str = None) -> dict[str, Any]:
        if query is None:
            data = self.data
        else:
            data = self.data.query(query)

        x: Series
        sx: Optional[Series] = None
        y: Series
        sy: Series

        if has_uncertainty(data[self.column_names["x"]]):
            x = data[self.column_names["x"]].apply(lambda x: x.nominal_value)
            sx = data[self.column_names["x"]].apply(lambda x: x.std_dev)
        else:
            x = data[self.column_names["x"]]
            if (name := self.column_names.get("x error")) is not None:
                sx = data[name]
        if has_uncertainty(data[self.column_names["y"]]):
            y = data[self.column_names["y"]].apply(lambda x: x.nominal_value)
            sy = data[self.column_names["y"]].apply(lambda x: x.std_dev)
        else:
            y = data[self.column_names["y"]]
            sy = data[self.column_names["y error"]]

        fitting_data: Dict[str, array | Optional[array]] = {
            "x": x,
            "y": y,
            "sy": sy,
            "sx": sx,
        }

        return fitting_data
