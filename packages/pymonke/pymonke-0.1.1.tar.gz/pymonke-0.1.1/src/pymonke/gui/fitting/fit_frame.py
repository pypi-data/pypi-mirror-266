from customtkinter import CTkFrame, CTkOptionMenu

from typing import Any, Optional

from .add_args_frame import AddArgsFrame
from ..formula.formula_frame import FormulaFrame
from .fit_option_menu import FitComboBox
from ..list_frame import ListFrame
from ..misc import get_meta, get_root
from ..plot.limits_frame import LimitsFrame
from ..dict_frame import DictFrame


class FitFrame(CTkFrame):
    def __init__(self, **kwargs: Any) -> None:
        CTkFrame.__init__(self, **kwargs)
        self.formula_frame = FormulaFrame(master=self, width=6000)
        self.formula_frame.grid(row=0, column=0, sticky="nsew", columnspan=2)
        self.formula_frame.entry_bindings = [self.update_to_meta,
                                             self.update_start_parameter_entries_from_formula_frame]
        self.grid_columnconfigure(0, weight=3)
        self.grid_rowconfigure(0, weight=5)
        self.grid_rowconfigure((1, 2, 3, 4), weight=1)
        self.grid_columnconfigure(1, weight=2)

        self.fit_meta: Optional[dict[str, Any]] = None

        self.fit_combo_box = FitComboBox(master=self)
        self.fit_combo_box.selection_bindings = [self.set_fit_meta, self.load_from_fit_meta,
                                                 self.update_start_parameter_entries_from_formula_frame]
        self.fit_combo_box.return_bindings = [self.set_fit_meta, self.load_from_fit_meta,
                                              self.update_start_parameter_entries_from_formula_frame]
        self.fit_combo_box.grid(row=1, column=0, sticky="w")

        self.fit_type_option = CTkOptionMenu(master=self, values=["OLS", "ODR"], command=self.update_to_meta)
        self.fit_type_option.set("OLS")
        self.fit_type_option.grid(row=1, column=1, sticky="e")

        self.start_parameter_frame = ListFrame(text="Start Parameters", has_add_button=False, master=self)
        self.start_parameter_frame.entry_bindings = [self.update_start_parameters]
        self.start_parameter_frame.grid(row=2, column=0, columnspan=1, pady=0)

        self.limits_frame = LimitsFrame(master=self, label="Fitting Limits")
        self.limits_frame.entry_bindings = [self.update_to_meta]
        self.limits_frame.grid(row=3, column=0, columnspan=1)

        self.plot_limits_frame = LimitsFrame(master=self, label="Plotting Limits")
        self.plot_limits_frame.entry_bindings = [self.update_to_meta]
        self.plot_limits_frame.grid(row=4, column=0, columnspan=1)

        self.plotting_style_arguments = DictFrame(master=self, text="Plotting Style Arguments")
        self.plotting_style_arguments.grid(row=5, column=0, pady=20, columnspan=1)

        self.add_args_frame = AddArgsFrame(master=self, width=200)
        self.add_args_frame.grid(row=2, column=1, sticky="nsew", padx=5, rowspan=3, pady=20)

    def update_start_parameter_entries_from_formula_frame(self) -> None:
        params: list[str] = self.formula_frame.params

        # search for already set parameters in meta
        if (fit_meta := self.get_fit_meta()) is not None:
            if (start_parameters := fit_meta.get("start_parameters")) is not None:
                if len(start_parameters) == len(params):
                    self.start_parameter_frame.set_parameters(start_parameters)
                    return
        self.start_parameter_frame.set_parameters([0] * len(params))

    def set_param_values(self, values: dict[str, Any]) -> None:
        self.formula_frame.parameters.set_param_values(values)

    def set_params_values_from_results(self) -> None:
        fit_name = self.get_fit_name()
        if fit_name is not None:
            fit_result = get_root(self).fit_result
            if fit_result is not None:
                result = fit_result.get(fit_name)
                if result is not None:
                    get_root(self).get_fit_frame().set_param_values(result.as_dict(False))

    def get_fit_type(self) -> str:
        if self.fit_type_option.get() == "OLS":
            return "optimize.curve_fit"
        elif self.fit_type_option.get() == "ODR":
            return "odr"
        else:
            raise Exception("unknown fitting type")

    def set_fit_type(self, _type: str) -> None:
        if _type == "optimize.curve_fit":
            self.fit_type_option.set("OLS")
        elif _type == "odr":
            self.fit_type_option.set("ODR")

    def delete_all_fits(self) -> None:
        for opt in self.fit_combo_box.cget("values"):
            if opt != "Add Fit":
                self.fit_combo_box.delete_option(opt)

    def update_to_meta(self, _: Any = None) -> None:
        """update meta from all child objects"""
        if self.fit_meta is None:
            return
        update = {
            "fit_type": self.get_fit_type(),
            "function": self.formula_frame.text,
            "x_min_limit": self.limits_frame.min,
            "x_max_limit": self.limits_frame.max,
            "plot_x_min_limit": self.plot_limits_frame.min,
            "plot_x_max_limit": self.plot_limits_frame.max,
            "start_parameters": self.get_start_parameters()
        }

        self.fit_meta.update(update)

    # -----------------------------------------------------------------------------
    # -------------------------Fit Combo Box---------------------------------------
    # -----------------------------------------------------------------------------

    def get_fit_name(self) -> Optional[str]:
        if (val := self.fit_combo_box.selected) == "Add Fit":
            return None
        else:
            return val

    def get_fit_meta(self) -> Optional[dict[str, Any]]:
        if (val := self.fit_combo_box.selected) == "Add Fit":
            return None
        else:
            ret = get_meta(self)["fits"][val]
            assert isinstance(ret, dict)
            return ret

    def set_fit_meta(self) -> None:
        """Set self.fit_meta to the meta dictionary that corresponds to the fit set in the combo box."""
        self.fit_meta = self.get_fit_meta()
        if self.fit_meta is None:
            self.plotting_style_arguments.meta = None
            self.add_args_frame.meta = None
            return
        if (meta := self.fit_meta.get("plotting_style")) is None:
            self.fit_meta["plotting_style"] = dict()
            meta = self.fit_meta["plotting_style"]
        self.plotting_style_arguments.meta = meta
        self.add_args_frame.meta = self.fit_meta

    def get_start_parameters(self) -> list[float]:
        p0: list[float] = []
        for param in self.start_parameter_frame.get_list():
            if param == "":
                p0.append(0)
            else:
                p0.append(float(param))

        return p0

    def update_start_parameters(self, _: Any = None) -> None:
        p0 = self.get_start_parameters()

        if self.fit_meta is not None:
            self.fit_meta.update({"start_parameters": p0})

    # -----PLOTTING-STYLE-----------------------------------------------------------
    def get_plotting_style_arguments(self) -> dict[str, float | str]:
        return self.plotting_style_arguments.get_args()

    def load_plotting_style_arguments_from_fit_meta(self) -> None:
        if (fit_name := self.get_fit_name()) is None:
            return
        fit_meta = get_meta(self)["fits"][fit_name]
        if (plotting_style := fit_meta.get("plotting_style")) is not None:
            self.plotting_style_arguments.load_parameters(plotting_style)

    def update_plotting_style(self) -> None:
        if (val := self.get_fit_name()) is None:
            return
        args = self.get_plotting_style_arguments()
        if get_meta(self)["fits"][val].get("plotting_style") is None:
            get_meta(self)["fits"][val]["plotting_style"] = args
        else:
            get_meta(self)["fits"][val]["plotting_style"].update(args)

    def load_limits_from_fit_meta(self) -> None:
        if (val := self.get_fit_name()) is None:
            return
        d = get_meta(self)["fits"][val]
        self.limits_frame.min = d.get("x_min_limit")
        self.limits_frame.max = d.get("x_max_limit")
        self.plot_limits_frame.min = d.get("plot_x_min_limit")
        self.plot_limits_frame.max = d.get("plot_x_max_limit")
        self.set_params_values_from_results()

    def load_from_fit_meta(self, _: Any = None) -> None:
        """if Values exist in meta[fit_name]. load them in."""
        if (fit := self.get_fit_meta()) is None:
            self.formula_frame.text = ""
            self.plotting_style_arguments.load_parameters({})
            self.limits_frame.set_limits(None, None)
            self.plot_limits_frame.set_limits(None, None)
            self.add_args_frame.load({
                "fit_points": None,
                "absolute_sigma": False,
                "check_finite": False,
            })
            self.fit_type_option.set("OLS")
            return
        if (func := fit.get("function")) is None:
            func = ""
        self.formula_frame.text = func
        if (fit_type := fit.get("fit_type")) is not None:
            self.set_fit_type(fit_type)
        else:
            self.set_fit_type("OLS")
        self.load_limits_from_fit_meta()
        self.load_plotting_style_arguments_from_fit_meta()
        self.update_start_parameter_entries_from_formula_frame()
        self.add_args_frame.load_from_meta()

    def update_from_to_meta(self, _: Any = None) -> None:
        self.load_from_fit_meta()
        self.update_to_meta()

    def load_from_meta(self, _: Any = None) -> None:
        meta = get_meta(self)
        if (fits := meta.get("fits")) is not None:
            if len(fits) >= 1:
                self.fit_combo_box.configure(values=[*(keys := list(fits.keys())), "Add Fit"])
                self.fit_combo_box.set(keys[0])
                self.fit_combo_box.selected = keys[0]
                self.set_fit_meta()
                self.load_from_fit_meta()
