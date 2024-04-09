from customtkinter import CTkFrame, CTkEntry, StringVar, CTkButton

from typing import Any

from .misc import browse_files


class BrowseFrame(CTkFrame):
    def __init__(self, file_type: str, placeholder: str = "Enter the file path", browse_text: str = "browse",
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.type = file_type
        self.file_path = StringVar(master=self, value=None)
        self.entry = CTkEntry(master=self, placeholder_text=placeholder, width=200)
        self.entry.bind("<Leave>", self.__check_text_if_empty)
        self.entry.grid(row=0, column=0, sticky="w")

        self.button = CTkButton(master=self, text=browse_text, command=self.browse, width=40)
        self.button.grid(row=0, column=1)

    def browse(self) -> Any:
        self.entry.configure(textvariable=self.file_path)
        self.file_path.set(browse_files("select Data file", self.type))

    def __check_text_if_empty(self, _: Any = None) -> Any:
        if self.file_path.get() == "":
            self.entry.configure(textvariable=None)
        else:
            self.entry.configure(textvariable=self.file_path)
