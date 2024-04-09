from customtkinter import CTkLabel

from typing import Any


class InfoLabel(CTkLabel):
    def __init__(self, **kwargs: Any) -> None:
        CTkLabel.__init__(self, **kwargs)

    def show_info(self, text: str) -> None:
        self.configure(text=text, text_color="green")

    def show_error(self, text: str) -> None:
        self.configure(text=text, text_color="red")
