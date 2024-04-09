from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkEntry, StringVar
from tkinter import Event

from typing import Callable, Any

from .misc import get_root


class ListFrame(CTkFrame):
    def __init__(self, text: str, has_add_button: bool = True, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.label = CTkLabel(self, text=text)
        self.label.grid(row=0, column=0)

        self.has_add_button = has_add_button
        if has_add_button:
            self.add_button = CTkButton(master=self, text="Add", command=self.add_parameter)
            self.add_button.grid(row=1, column=0)

        self.entries: list[Entry] = []

        self.text_list: list[str] = []

        self.entry_bindings: list[Callable[[], None]] = []

    def get_selected_index(self, event: "Event[Any]") -> int:
        name = str(event.widget).removesuffix(".!entry")
        widget = get_root(self).nametowidget(name)  # type: ignore
        res: int = widget.grid_info()["row"] - 1
        return res

    def up(self, event: "Event[Any]") -> None:
        index: int = self.get_selected_index(event) - 1
        if index >= 0:
            self.entries[index].focus_set()

    def down(self, event: "Event[Any]") -> None:
        index: int = self.get_selected_index(event) + 1
        if index < len(self.entries):
            self.entries[index].focus_set()

    def add_parameter(self, val: Any = "") -> None:
        n = len(self.entries)
        entry = Entry(master=self, text=str(val))
        entry.grid(row=n+1, column=0)
        entry.bind("<Return>", self._update_list)
        for func in self.entry_bindings:
            entry.bind("<Return>", func)
            entry.bind("<Up>", self.up)
            entry.bind("<Down>", self.down)
        self.entries.append(entry)
        if self.has_add_button:
            self.add_button.grid(row=n+2, column=0)

    def set_parameters(self, parameters: list[Any]) -> Any:
        self.delete_all()
        for param in parameters:
            self.add_parameter(param)

    def delete_all(self) -> None:
        for entry in self.entries:
            entry.destroy()
        self.entries = []

    def _update_list(self, _: Any = None) -> None:
        self.text_list = self.get_list()

    def get_list(self) -> list[str]:
        return [i.string_var.get() for i in self.entries]


class Entry(CTkEntry):
    def __init__(self, text: str = "",  **kwargs: Any) -> None:
        self.string_var = StringVar(value=text)
        super().__init__(textvariable=self.string_var, **kwargs)
