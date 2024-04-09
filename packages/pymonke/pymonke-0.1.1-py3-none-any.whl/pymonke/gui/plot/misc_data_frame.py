from customtkinter import CTkFrame, CTkCheckBox

import json
from typing import Any, Optional, AnyStr

from ..labeled_entry import LabeledEntry
from ..misc import get_meta


def dumps(obj: Any) -> str:
    obj = json.dumps(obj)
    ret = obj.replace("[", "").replace("]", "").replace(" ", "").replace("'", "").replace('"', "")
    assert isinstance(ret, str)
    return ret


class MiscDataFrame(CTkFrame):
    def __init__(self, meta: Optional[dict[str, Any]] = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.figure_style_entry = LabeledEntry(master=self, label="Figure style")
        self.figure_style_entry.entry.bind("<Return>", self.callback)
        self.figure_style_entry.grid(row=0, column=0, pady=5)

        self.figure_size_entry = LabeledEntry(master=self, label="Figure size")
        self.figure_size_entry.entry.bind("<Return>", self.callback)
        self.figure_size_entry.grid(row=1, column=0, pady=5)

        self.dpi_entry = LabeledEntry(master=self, label="DPI")
        self.dpi_entry.entry.bind("<Return>", self.callback)
        self.dpi_entry.grid(row=0, column=1, pady=5)

        self.label_entry = LabeledEntry(master=self, label="Label")
        self.label_entry.entry.bind("<Return>", self.callback)
        self.label_entry.grid(row=1, column=1, pady=5)

        self.latex_check_box = CTkCheckBox(master=self, text="Latex", command=self.callback)
        self.latex_check_box.grid(row=2, column=0, pady=5)

        self.meta = meta

    def callback(self, _: Any = None) -> None:
        # self.update_figure_style(self.figure_style_entry.text_var.get())
        figure_style: Optional[list[str]] = self.set_figure_style(self.figure_style_entry.text_var.get())
        figure_size: Optional[tuple[float, float]] = self.set_figure_size(self.figure_size_entry.text_var.get())
        dpi: Optional[float] = self.set_dpi(self.dpi_entry.text_var.get())
        label: str = self.get_label()
        latex: bool = bool(self.latex_check_box.get())
        data = {
            "figure_style": figure_style,
            "figure_size": figure_size,
            "figure_dpi": dpi,
            "label": label,
            "latex": latex,
        }

        if self.meta is not None:
            self.meta.update(data)

    def load_from_meta(self) -> None:
        if self.meta is None:
            return
        self.set_figure_style((self.meta.get("figure_style") or ""))
        self.set_figure_size(self.meta.get("figure_size") or "")
        self.set_dpi(self.meta.get("figure_dpi") or "")
        self.set_label(self.meta.get("label") or "")
        if self.meta.get("latex") or False:
            self.latex_check_box.select()
        else:
            self.latex_check_box.deselect()

    def get_figure_style(self) -> list[str]:
        text = self.figure_style_entry.text
        ret = text.split(",")
        assert isinstance(ret, list)
        return ret

    def set_figure_style(self, text: str | Any) -> Optional[list[str]]:
        if text is None:
            return None
        if not isinstance(text, str):
            text = dumps(text)
        if text == "":
            self.figure_style_entry.text = ""
            self.figure_style_entry.text_var.set("")
            return None
        self.figure_style_entry.text = text
        self.figure_style_entry.text_var.set(text)
        ret = text.split(",")
        assert isinstance(ret, list)
        return ret

    def get_figure_size(self) -> Optional[tuple[float, float]]:
        return self.set_figure_size(self.figure_size_entry.text)

    def set_figure_size(self, text: str) -> Optional[tuple[float, float]]:
        if text is None:
            return None
        if not isinstance(text, str):
            text = dumps(text)
        entry = self.figure_size_entry
        if text == "":
            entry.text = ""
            entry.text_var.set("")
            return None
        try:
            ret = text.split(",")
            assert len(ret) == 2 and isinstance(ret, list)
            res = float(ret[0]), float(ret[1])
            entry.text_var.set(text)
            entry.text = text
            return res[0], res[1]
        except (AssertionError, ValueError):
            entry.text_var.set(entry.text)
            return self.get_figure_size()

    def get_dpi(self) -> Optional[float]:
        return self.set_dpi(self.dpi_entry.text)

    def set_dpi(self, text: str) -> Optional[float]:
        entry = self.dpi_entry
        if text == "":
            entry.text = ""
            entry.text_var.set("")
            return None
        try:
            val = float(text)
            entry.text = text
            entry.text_var.set(text)
            return val
        except ValueError:
            entry.text_var.set(entry.text)
            return self.get_dpi()

    def set_label(self, text: str) -> str:
        self.label_entry.text = text
        self.label_entry.text_var.set(text)
        return text

    def get_label(self) -> str:
        return self.set_label(self.label_entry.text_var.get())

