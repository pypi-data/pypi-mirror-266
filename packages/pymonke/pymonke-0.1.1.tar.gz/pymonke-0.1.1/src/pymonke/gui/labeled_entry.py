from customtkinter import CTkLabel, CTkEntry, CTkFrame, StringVar

from typing import Any, Optional, Type


class LabeledEntry(CTkFrame):
    def __init__(self, label: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.text_var = StringVar(value="")
        self.text = ""

        self.grid_columnconfigure(0, weight=1)

        self.label = CTkLabel(self, text=label)
        self.label.grid(row=0, column=0)

        self.entry = CTkEntry(self, textvariable=self.text_var)
        self.entry.grid(row=1, column=0)
