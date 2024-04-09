from customtkinter import CTkFrame, CTkButton, CTkLabel
from collections import deque

from typing import Any


class StatusFrame(CTkFrame):
    def __init__(self, max_length: int = 10, **kwargs: Any) -> None:
        CTkFrame.__init__(self, **kwargs)
        self.max_length = max_length
        self.labels: deque[CTkLabel] = deque()
        self.button = CTkButton(self, text="Clear", command=self.clear)
        self.grid_rowconfigure(tuple(range(max_length + 1)), minsize=25)
        self.button.grid(row=max_length, column=0)

    def add_info(self, text: str) -> None:
        self.add_text(text, "green")

    def add_error(self, text: str) -> None:
        self.add_text(text, "red")

    def add_text(self, text: str, color: str) -> None:
        if len(self.labels) == self.max_length:
            self.delete_first()
        label = CTkLabel(master=self, text=text, text_color=color, height=25)
        label.grid(row=len(self.labels), column=0, sticky="ew")
        self.labels.append(label)
        self.button.grid(row=self.max_length, column=0)

    def delete_first(self) -> None:
        self.labels[0].destroy()
        self.labels.popleft()
        for i, label in enumerate(self.labels):
            label.grid(row=i, column=0, sticky="ew")

    def clear(self) -> None:
        while len(self.labels) > 0:
            self.delete_first()
