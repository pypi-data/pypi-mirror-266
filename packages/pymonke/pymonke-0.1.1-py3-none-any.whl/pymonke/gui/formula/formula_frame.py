from customtkinter import CTkFrame, CTkEntry, CTkLabel

import sys
from tkinter import StringVar
from typing import Optional, Callable, Any

from pymonke.fit.parse import parse_function, replace_funcs
from pymonke.fit.fit import func_type
from ..misc import EntryError
from .parameters_scrollable_frame import ParametersScrollableFrame


class FormulaFrame(CTkFrame):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.__text = StringVar(master=self, value="", name="FormulaFrameText")
        self.function: Optional[func_type] = None
        self.params: list[str] = []

        self.configure(height=5000, width=1000)
        self.grid_rowconfigure((0, 2), weight=1)
        self.grid_rowconfigure(1, weight=20)
        self.grid_columnconfigure(0, weight=1)

        self.entry = CTkEntry(master=self, placeholder_text="Enter your formula", textvariable=self.__text,
                              width=self.master["width"])
        self.entry.grid(row=0, column=0, sticky="ew", padx=10)

        self.entry.bind(sequence="<Return>", command=self.entry_callback)
        self.entry_bindings: list[Callable[[], None]] = []

        self.error_label = CTkLabel(master=self, text="")
        self.error_label.configure(text_color="red")
        self.error_label.grid(row=2, column=0, sticky="we", padx=10)

        self.parameters = ParametersScrollableFrame(master=self, width=200)
        self.parameters.grid(row=1, column=0, sticky="ns")

    @property
    def text(self) -> str:
        return self.__text.get()

    @text.setter
    def text(self, _formula: str) -> None:
        try:
            self.__text.set(replace_funcs(_formula))
            if _formula == "":
                self.function, self.params = None, []
            else:
                self.function, self.params = parse_function(self.text)
            self.reset_error_label()
        except SyntaxError:
            self.set_error_label("Invalid Entry")
            return

        self.parameters.generate_parameter_frames(self.params)

    def entry_callback(self, _event: Any = None) -> None:
        self.text = self.text
        for binding in self.entry_bindings:
            binding()

    def rename(self) -> None:
        formula: str = self.__text.get()
        try:
            new = self.parameters.rename_entries(formula)
            self.__text.set(new)
            self.entry_callback()
            self.reset_error_label()
        except EntryError as e:
            self.set_error_label(str(e))
        except Exception as e:
            print(e, file=sys.stderr)
            exit(-1)

    def reset_error_label(self) -> None:
        self.error_label.configure(text="")

    def set_error_label(self, text: str) -> None:
        self.error_label.configure(text=text)
