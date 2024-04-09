from customtkinter import CTkFrame
import pandas as pd

import json
from typing import Any, Optional

from .browse_save_frame import BrowseSaveFrame
from ..browse_frame import BrowseFrame
from ..entry_label_frame import EntryLabelFrame
from ..fitting.fit_frame import FitFrame
from ..misc import get_root
from ..misc import get_data, get_meta, get_root
from .status_frame import StatusFrame

from pymonke.misc.file_management import read_data_into_dataframe
from pymonke.misc.dataframe import get_error_column_name


class DataInitFrame(CTkFrame):
    def __init__(self, **kwargs: Any) -> None:
        CTkFrame.__init__(self, **kwargs)

        self.browse_data_frame = BrowseFrame(file_type="*.csv; *.txt", master=self, placeholder="Enter the data file")
        self.browse_data_frame.grid(row=0, column=0, columnspan=2)

        self.load_meta_frame = BrowseFrame(file_type=".json", master=self, browse_text="load",
                                           placeholder="Enter the meta data for plotting")
        self.load_meta_frame.grid(row=1, column=0, columnspan=2)

        self.x_data_frame = EntryLabelFrame(master=self, label="X")
        self.x_data_frame.entry.bind("<Return>", self.save_x_name)
        self.x_data_frame.grid(row=2, column=0)
        self.y_data_frame = EntryLabelFrame(master=self, label="Y")
        self.y_data_frame.entry.bind("<Return>", self.save_y_name)
        self.y_data_frame.grid(row=2, column=1)

        self.status = StatusFrame(master=self, height=400)
        self.status.grid(row=4, column=0, columnspan=2, sticky="ns")

        self.save_meta_frame = BrowseSaveFrame(master=self)
        self.save_meta_frame.save_button.configure(command=self.save_meta_to_file)
        self.save_meta_frame.grid(row=3, column=0, columnspan=2)

    def load_data(self, browse: bool = True) -> Optional[pd.DataFrame]:
        try:
            if browse:
                self.browse_data_frame.browse()
            file_path = self.browse_data_frame.file_path.get()
            if (kwargs := get_meta(self).get("read_data_args")) is None:
                kwargs = dict()
            data = read_data_into_dataframe(file_path, **kwargs)
            get_meta(self)["file"] = file_path
            self.status.add_info(text="data loaded successfully")
            return data
        except Exception as e:
            self.status.add_error(str(e))
            return None

    def load_meta(self) -> Optional[dict[str, Any]]:
        try:
            fit_frame: FitFrame = get_root(self).get_fit_frame()
            fit_frame.delete_all_fits()
            self.load_meta_frame.browse()
            file_path = self.load_meta_frame.file_path.get()
            data: dict[str, Any] = json.loads(open(file_path).read())
            self.status.add_info("Meta Data loaded successfully")
            return data
        except Exception as e:
            self.status.add_error(str(e))
            return None

    def check_xy_input(self, xy: str) -> None:
        if "x" in xy:
            if (text := self.x_data_frame.text.get()) is not None and self.entry_in_dataframe(text):
                self.status.add_info("X column found")
            else:
                self.status.add_error("X column not found")
        if "y" in xy:
            if (text := self.y_data_frame.text.get()) is not None and self.entry_in_dataframe(text):
                self.status.add_info("Y column found")
                data = get_data(self)
                assert isinstance(data, pd.DataFrame)
                if get_error_column_name(data, text) is None:
                    self.status.add_error("Y Error not found")

            else:
                self.status.add_error("Y column not found")

    def entry_in_dataframe(self, name: str) -> bool:
        if (data := get_data(self)) is not None:
            return name in data
        else:
            return False

    def save_x_name(self, _: Any = None) -> None:
        x_name = self.x_data_frame.text.get()
        get_meta(self)["x"] = x_name
        self.check_xy_input("x")
        get_root(self).get_plot_frame().plot_data()

    def save_y_name(self, _: Any = None) -> None:
        y_name = self.y_data_frame.text.get()
        get_meta(self)["y"] = y_name
        self.check_xy_input("y")
        get_root(self).get_plot_frame().plot_data()

    def load_from_meta(self) -> None:
        """Function that initializes values in this frame if metadata is loaded."""
        meta = get_meta(self)
        if (file := meta.get("file")) is not None:
            self.browse_data_frame.file_path.set(file)
            get_root(self).data = self.load_data(False)

        if (x := meta.get("x")) is not None:
            self.x_data_frame.text.set(x)
        if (y := meta.get("y")) is not None:
            self.y_data_frame.text.set(y)
        self.check_xy_input("xy")

    def save_meta_to_file(self) -> None:
        try:
            self.save_meta_frame.save()
            self.status.add_info("Meta data saved to file successfully")
        except Exception as e:
            self.status.add_error(str(e))
