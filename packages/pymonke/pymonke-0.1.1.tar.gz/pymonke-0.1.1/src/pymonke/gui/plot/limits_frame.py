from customtkinter import CTkFrame, StringVar, CTkEntry, CTkLabel

from typing import Callable, Any, Optional
from ..misc import get_meta


class LimitsFrame(CTkFrame):
    def __init__(self, label: str = "", meta: Optional[dict[str, Any]] = None, max_lim_key: Optional[str] = None,
                 min_lim_key: Optional[str] = None, **kwargs: Any) -> None:
        CTkFrame.__init__(self, **kwargs)
        if label != "":
            self.label = CTkLabel(master=self, text=label)
            self.label.grid(row=0, column=0, columnspan=2)

        self.min_var = StringVar(value="")
        self.max_var = StringVar(value="")
        self.__min: Optional[float] = None
        self.__max: Optional[float] = None
        self.set_limits(None, None)

        self.entry_bindings: list[Callable[[], None]] = []

        # Define a dictionary where to store the limits on change with the corresponding keys
        self.meta: Optional[dict[str, Any]] = meta
        self.max_lim_key: Optional[str] = max_lim_key
        self.min_lim_key: Optional[str] = min_lim_key

        self.min_entry = CTkEntry(self, textvariable=self.min_var)
        self.min_entry.bind("<Return>", command=self.callback)
        self.max_entry = CTkEntry(self, textvariable=self.max_var)
        self.max_entry.bind("<Return>", command=self.callback)

        self.min_entry.grid(row=1, column=0)
        self.max_entry.grid(row=1, column=1)

    @property
    def min(self) -> Optional[float]:
        return self.__min

    @min.setter
    def min(self, value: Optional[float]) -> None:
        if value is None:
            self.__min = None
            self.min_var.set("")
        else:
            self.__min = value
            self.min_var.set(str(value))

    def get_min_var(self) -> Optional[float]:
        if (val := self.min_var.get()) == "":
            return None
        else:
            return float(val)

    def get_max_var(self) -> Optional[float]:
        if (val := self.max_var.get()) == "":
            return None
        else:
            return float(val)

    @property
    def max(self) -> Optional[float]:
        return self.__max

    @max.setter
    def max(self, value: Optional[float]) -> None:
        if value is None:
            self.__max = None
            self.max_var.set("")
        else:
            self.__max = value
            self.max_var.set(str(value))

    def set_limits(self, _min: Optional[float], _max: Optional[float]) -> None:
        self.min = _min
        self.max = _max

    def set_min(self, value: Optional[float]) -> None:
        if self.max is not None and value is not None:
            if value >= self.max:
                self.min = self.min
                return

        self.min = value

    def set_max(self, value: Optional[float]) -> None:
        if self.min is not None and value is not None:
            if value <= self.min:
                self.max = self.max
                return
        self.max = value

    def callback(self, _event: Any = None) -> None:
        self.set_max(self.get_max_var())
        self.set_min(self.get_min_var())
        if self.meta is not None:
            assert isinstance(self.min_lim_key, str) and isinstance(self.max_lim_key, str)
            ret = {
                self.min_lim_key: self.min,
                self.max_lim_key: self.max,
            }

            self.meta.update(ret)
        for binding in self.entry_bindings:
            binding()
