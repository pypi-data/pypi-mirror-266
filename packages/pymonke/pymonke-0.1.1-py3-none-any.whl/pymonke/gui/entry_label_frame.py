from customtkinter import CTkFrame, CTkLabel, CTkEntry, StringVar

from functools import partial
from typing import Any


class EntryLabelFrame(CTkFrame):
    """A Frame with an entry next to a label"""

    def __init__(self, placeholder: str = "Entry", label: str = "Label", left_label: bool = True,
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.text = StringVar(master=self)
        self.label = CTkLabel(self, text=label)
        self.entry = CTkEntry(self, placeholder_text=placeholder, textvariable=self.text)
        # self.entry.bind("<Leave>", self.check_text_if_empty)
        label_grid = partial(self.label.grid, row=0, padx=5)
        if left_label:
            label_grid(column=0)
            self.entry.grid(row=0, column=1)
        else:
            label_grid(column=1)
            self.entry.grid(row=0, column=0)

    def check_text_if_empty(self, _: Any = None) -> None:
        if self.text.get() == "":
            self.entry.configure(textvariable=None)
        else:
            self.entry.configure(textvariable=self.text)
