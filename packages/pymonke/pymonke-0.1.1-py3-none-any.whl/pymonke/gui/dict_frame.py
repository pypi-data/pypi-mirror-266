from customtkinter import CTkFrame, CTkEntry, CTkButton, CTkLabel, StringVar
from tkinter import Event, INSERT
from typing import Optional, Any, Callable

from .misc import get_root


class EntryPairFrame(CTkFrame):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.key_var = StringVar()
        self.key = CTkEntry(master=self, textvariable=self.key_var)
        self.key.grid(row=0, column=0)

        self.value_var = StringVar()
        self.value = CTkEntry(master=self, textvariable=self.value_var)
        self.value.grid(row=0, column=1)

        self.delete_button = CTkButton(master=self, text="-", width=30, command=self.destroy)
        self.delete_button.grid(row=0, column=2)


class DictFrame(CTkFrame):
    def __init__(self, text: str, meta: Optional[dict[str, Any]] = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.meta = meta
        self.label = CTkLabel(self, text=text)
        self.label.grid(row=0, column=0)

        self.add_button = CTkButton(master=self, text="Add", command=self.add_parameter)
        self.add_button.grid(row=1, column=0)

        self.entries: list[EntryPairFrame] = []

        self.return_bindings: list[Callable[[], None]] = []
        self.ignore_keys: list[str] = []

    def add_parameter(self, key: str = "", value: str = "") -> None:
        n = len(self.entries)
        entry = EntryPairFrame(master=self)
        entry.key.bind("<Return>", self.bindings)
        entry.key.bind("<Right>", self.right)
        entry.key.bind("<Up>", self.up)
        entry.key.bind("<Down>", self.down)
        entry.key_var.set(key)

        entry.value.bind("<Return>", self.bindings)
        entry.value.bind("<Left>", self.left)
        entry.value.bind("<Up>", self.up)
        entry.value.bind("<Down>", self.down)
        entry.value_var.set(value)

        entry.grid(row=n + 1, column=0)
        entry.delete_button.configure(command=lambda: self.delete_on_button_click(entry))

        self.entries.append(entry)
        self.add_button.grid(row=n + 2, column=0)

    def left(self, event: "Event[Any]") -> None:
        if event.widget.index(INSERT) > 0:
            return
        key_widget: str = str(event.widget).removesuffix("2.!entry") + ".!entry"
        get_root(self).nametowidget(key_widget).focus_set()  # type: ignore

    def right(self, event: "Event[Any]") -> None:
        if len(event.widget.get()) > event.widget.index(INSERT):
            return
        value_widget: str = str(event.widget).removesuffix(".!entry") + "2.!entry"
        get_root(self).nametowidget(value_widget).focus_set()  # type: ignore

    def get_index_from_selected(self, event: "Event[Any]") -> tuple[int, int]:
        widget = str(event.widget).removesuffix(".!entry")
        if widget[-1] == "2":
            col = 1
            widget = widget.removesuffix(".!ctkentry2")
        else:
            col = 0
            widget = widget.removesuffix(".!ctkentry")
        row = get_root(self).nametowidget(widget).grid_info()["row"]  # type: ignore
        return row, col

    def up(self, event: "Event[Any]") -> None:
        row, col = self.get_index_from_selected(event)
        row -= 2
        if row < 0 or row >= len(self.entries):
            return
        entry = self.entries[row]
        if not col:
            entry.key.focus_set()
        else:
            entry.value.focus_set()

    def down(self, event: "Event[Any]") -> None:
        row, col = self.get_index_from_selected(event)
        if row >= len(self.entries) or row < 0:
            return
        entry = self.entries[row]
        if not col:
            entry.key.focus_set()
        else:
            entry.value.focus_set()

    def load_parameters(self, data: dict[str, str]) -> None:
        self.delete_all()
        for key in data.keys():
            val = data[key]
            if key not in self.ignore_keys:
                self.add_parameter(key, val)

    def delete_entry(self, index: int) -> None:
        entry = self.entries.pop(index)
        entry.destroy()
        for index, entry in enumerate(self.entries):
            entry.grid(row=index + 1, column=0)

    def delete_last(self) -> None:
        self.delete_entry(-1)

    def delete_all(self) -> None:
        for _ in range(len(self.entries)):
            self.delete_last()

    def delete_on_button_click(self, button: EntryPairFrame) -> None:
        """delete the Button and also remove the entry from meta if given"""
        key = button.key_var.get()
        index = button.grid_info()["row"] - 1
        if self.meta is not None:
            self.meta.pop(key)
        self.delete_entry(index)

    def get_args(self) -> dict[str, float | str]:
        res = dict()
        for entry in self.entries:
            if (val := entry.value_var.get()) == "":
                val = None
            res[entry.key_var.get()] = self.parse(val)

        return res

    def bindings(self, _: Any = None) -> None:
        self.update_meta()
        for binding in self.return_bindings:
            binding()

    def update_meta(self) -> None:
        if self.meta is None:
            return
        args = self.get_args()
        while self.meta != dict():
            self.meta.popitem()
        self.meta.update(args)

    def load_from_meta(self) -> None:
        if self.meta is None:
            return
        self.load_parameters(self.meta)

    def parse(self, value: str) -> float | str:
        try:
            return float(value)
        except:
            return value
