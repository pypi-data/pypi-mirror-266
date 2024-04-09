from customtkinter import CTkFrame, CTkCheckBox

from typing import Any, Optional

from ..labeled_entry import LabeledEntry


class AddArgsFrame(CTkFrame):
    def __init__(self, meta: Optional[dict[str, Any]] = None, **kwargs: Any) -> None:
        CTkFrame.__init__(self, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.fitting_points_entry = LabeledEntry(master=self, label="Fitting Points")
        self.fitting_points_entry.entry.bind("<Return>", self.fitting_points_entry_callback)
        self.fitting_points_entry.grid(row=0, column=0, pady=10, sticky="we")

        self.absolute_sigma_checkbox = CTkCheckBox(master=self, text="Absolute Sigma", command=self.update_values)
        self.absolute_sigma_checkbox.grid(row=1, column=0, sticky="w")

        self.check_finite_checkbox = CTkCheckBox(master=self, text="Check Finite", command=self.update_values)
        self.check_finite_checkbox.grid(row=2, column=0, sticky="w")

        self.label_entry = LabeledEntry(master=self, label="Label")
        self.label_entry.entry.grid_configure(sticky="we")
        self.label_entry.entry.bind("<Return>", self.update_values)
        self.label_entry.grid(row=3, column=0, sticky="we")

        self.meta: Optional[dict[str, Any]] = meta

    def get_values(self) -> dict[str, Any]:
        res = {
            "fit_points": self.get_fitting_points_entry(),
            "absolute_sigma": bool(self.absolute_sigma_checkbox.get()),
            "check_finite": bool(self.check_finite_checkbox.get()),
            "label": self.label_entry.text_var.get()
        }

        return res

    def update_values(self, _event: Any = None) -> None:
        res = self.get_values()
        if self.meta is not None:
            self.meta.update(res)

    def load_from_meta(self) -> None:
        if self.meta is not None:
            self.load(self.meta)

    def load(self, data: dict[str, Any]) -> None:
        self.set_fitting_points_entry(data.get("fit_points", None))
        self.update_fitting_points_entry()
        if data.get("absolute_sigma") or False:
            self.absolute_sigma_checkbox.select()
        else:
            self.absolute_sigma_checkbox.deselect()
        if data.get("check_finite") or False:
            self.check_finite_checkbox.select()
        else:
            self.check_finite_checkbox.deselect()
        self.label_entry.text_var.set(data.get("label") or "")

    def fitting_points_entry_callback(self, _: Any = None) -> None:
        self.update_fitting_points_entry()
        self.update_values()

    def get_fitting_points_entry(self) -> Optional[int]:
        text = self.fitting_points_entry.text_var.get()
        if text == "":
            return None
        else:
            return int(text)

    def set_fitting_points_entry(self, value: Optional[int]) -> None:
        if value is None:
            self.fitting_points_entry.text_var.set("")
        else:
            self.fitting_points_entry.text_var.set(str(value))
        self.update_fitting_points_entry()

    def update_fitting_points_entry(self) -> None:
        text = self.fitting_points_entry.text_var.get()
        if text == "":
            self.fitting_points_entry.text = ""
        try:
            _ = int(text)
            self.fitting_points_entry.text = text
        except ValueError as _:
            self.fitting_points_entry.text_var.set(self.fitting_points_entry.text)
