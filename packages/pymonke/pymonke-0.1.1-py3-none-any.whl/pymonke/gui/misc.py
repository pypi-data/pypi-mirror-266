from customtkinter import CTkBaseClass
import pandas as pd

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import os
from tkinter import filedialog
from typing import Any, Optional


class EntryError(Exception):
    """Error that occurs when trying to enter a text into an entry that is not supposed to be entered
    by the user."""

    def __init__(self, text: str = "Invalid Entry"):
        Exception.__init__(self, text)


def browse_files(text: str, file_type: str) -> str:
    """Search for a file in the file explorer."""
    filename = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select a File",
                                          filetypes=((text, file_type), ("all files", "*.*")))

    return filename


@dataclass
class Root:
    meta: dict[str, Any] = field(default_factory=dict)
    data: Optional[pd.DataFrame] = None
    fit_result: Optional[dict[str, Any]] = None

    @abstractmethod
    def load_from_meta(self) -> None:
        """Update everything based on the meta dictionary."""
        pass

    @abstractmethod
    def get_x(self) -> "Optional[pd.Series[float]]": pass

    @abstractmethod
    def get_y(self) -> "Optional[pd.Series[float]]": pass

    @abstractmethod
    def get_sx(self) -> "Optional[pd.Series[float]]": pass

    @abstractmethod
    def get_sy(self) -> "Optional[pd.Series[float]]": pass

    @abstractmethod
    def get_plot_frame(self) -> Any: pass

    @abstractmethod
    def do_fit(self) -> Any: pass

    @abstractmethod
    def get_fit_frame(self) -> Any: pass

    @abstractmethod
    def get_fit_meta(self) -> Optional[dict[str, Any]]: pass

    @abstractmethod
    def get_additional_arguments(self) -> dict[str, Any]: pass

    @abstractmethod
    def get_plotting_style_arguments(self) -> dict[str, Any]: pass

    def __lt__(self, other: Any) -> bool:
        assert isinstance(self.data, pd.DataFrame)
        return len(self.data) < len(other.data)

    def __hash__(self) -> int:
        return hash(1)


def get_meta(obj: CTkBaseClass) -> dict[str, Any]:
    """Get the metadata for data fitting by looking for a master object that has the meta attribute
    and is a subclass of Root."""
    master = obj.master
    while not isinstance(master, Root):
        master = master.master

    assert isinstance(master, Root)
    return master.meta


def get_data(obj: CTkBaseClass) -> Optional[pd.DataFrame]:
    """Get the metadata for data fitting by looking for a master object that has the meta attribute
    and is a subclass of Root."""
    master = obj.master
    while not isinstance(master, Root):
        master = master.master

    assert isinstance(master, Root)
    return master.data


def get_root(obj: CTkBaseClass) -> Root:
    """Get the Root object."""
    master = obj.master
    while not isinstance(master, Root):
        master = master.master

    assert isinstance(master, Root)
    return master
