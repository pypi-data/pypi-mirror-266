from customtkinter import CTkFrame, CTkButton

import json
from typing import Any

from pymonke.misc.pymonke_json_encoder import PyMonkeJSONEncoder
from ..data_init.browse_save_frame import BrowseSaveFrame
from ..dict_frame import DictFrame
from ..fitting.fit_frame import FitFrame
from ..info_label import InfoLabel
from .limits_frame import LimitsFrame
from ..misc import get_meta, get_root
from .misc_data_frame import MiscDataFrame
from .plot_canvas import PlotCanvas


class PlotFrame(CTkFrame):
    def __init__(self, **kwargs: Any) -> None:
        CTkFrame.__init__(self, **kwargs)
        self.canvas = PlotCanvas(master=self)
        self.canvas.grid(row=0, column=0, columnspan=3)

        self.x_limits_frame = LimitsFrame(master=self, label="X Limits", meta=get_meta(self),
                                          max_lim_key="x_max_limit", min_lim_key="x_min_limit")
        self.x_limits_frame.entry_bindings = [self.canvas.set_limits_from_meta]
        self.x_limits_frame.grid(row=1, column=0, columnspan=2)

        self.y_limits_frame = LimitsFrame(master=self, label="Y Limits", meta=get_meta(self),
                                          max_lim_key="y_max_limit", min_lim_key="y_min_limit")
        self.y_limits_frame.entry_bindings = [self.canvas.set_limits_from_meta]
        self.y_limits_frame.grid(row=2, column=0, columnspan=2)

        self.button = CTkButton(self, text="Fit Data", command=self.plot_data)
        self.button.grid(row=3, column=0, columnspan=2)

        self.info_label = InfoLabel(master=self, text="")
        self.info_label.grid(row=4, column=0, columnspan=3, pady=5)

        if get_meta(self).get("plotting_style") is None:
            get_meta(self)["plotting_style"] = dict()
        self.plotting_arguments = DictFrame(master=self, text="Plotting arguments",
                                            meta=get_meta(self)["plotting_style"])
        self.plotting_arguments.grid(row=5, column=0, columnspan=2, pady=5, padx=10)

        self.misc_data_frame = MiscDataFrame(master=self)
        self.misc_data_frame.meta = get_meta(self)
        self.misc_data_frame.grid(row=1, column=2, rowspan=2)

        self.save_results_frame = BrowseSaveFrame(master=self)
        self.save_results_frame.save_button.configure(command=self.save_results)
        self.save_results_frame.grid(row=5, column=2, padx=10)

    def plot_data(self) -> None:
        try:
            self.canvas.plot_data()
            _min, _max = self.canvas.ax.get_xlim()
            self.x_limits_frame.set_limits(_min, _max)
            self.info_label.show_info("Plotting the data and/or fitting successful.")
        except Exception as e:
            self.info_label.show_error(e.__repr__())

        # show parameter values after the fit
        fit_frame: FitFrame = get_root(self).get_fit_frame()
        fit_frame.set_params_values_from_results()

    def load_from_meta(self) -> None:
        self.plot_data()
        meta = get_meta(self)
        _min, _max = meta.get("x_min_limit"), meta.get("x_max_limit")
        if _min is not None:
            self.x_limits_frame.set_min(_min)
        if _max is not None:
            self.x_limits_frame.set_max(_max)
        self.canvas.set_x_limits(_min, _max)

        if get_meta(self).get("plotting_style") is None:
            get_meta(self)["plotting_style"] = dict()
        self.plotting_arguments.meta = get_meta(self)["plotting_style"]
        self.plotting_arguments.load_from_meta()
        self.misc_data_frame.load_from_meta()

    def load_limits_to_meta(self, _: Any = None) -> None:
        _min = float(self.x_limits_frame.min_var.get())
        _max = float(self.x_limits_frame.max_var.get())
        get_meta(self)["x_min_limit"] = _min
        get_meta(self)["x_max_limit"] = _max

    def save_results(self) -> None:
        try:
            results = get_root(self).fit_result
            ret = dict()
            if results is None:
                return
            for key in results.keys():
                ret[key] = results[key].as_dict(True)  # type: ignore

            text = json.dumps(ret, indent=2, cls=PyMonkeJSONEncoder)
            file = self.save_results_frame.browse_frame.file_path.get()
            with open(file, "w") as f:
                f.write(text)
            self.info_label.show_info("Results saved successfully.")
        except Exception as e:
            self.info_label.show_error(e.__repr__())


