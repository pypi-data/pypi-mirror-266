from customtkinter import CTkFrame, CTkButton

import json
from typing import Any

from ..browse_frame import BrowseFrame
from ..misc import get_meta


class BrowseSaveFrame(CTkFrame):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.save_button = CTkButton(master=self, text="Save", width=30, command=self.save)
        self.save_button.grid(row=0, column=0)

        self.browse_frame = BrowseFrame(master=self, file_type=".*")
        self.browse_frame.grid(row=0, column=1)

    def save(self) -> None:
        file = self.browse_frame.file_path.get()
        with open(file, "w") as f:
            _input: str = json.dumps(get_meta(self), indent=4)
            f.write(_input)
