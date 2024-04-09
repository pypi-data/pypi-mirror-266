from customtkinter import CTkScrollableFrame

from typing import Optional, Any

from pymonke.fit.parse import rename_parameters, RepetitionError
from .parameter_frame import ParameterFrame
from ..misc import EntryError


class ParametersScrollableFrame(CTkScrollableFrame):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.param_frames: dict[str, ParameterFrame] = dict()

    def generate_parameter_frames(self, params: list[str]) -> None:
        self.delete_parameter_frames()

        for index, param in enumerate(params):
            self.param_frames[param] = ParameterFrame(master=self, name=param)
            self.param_frames[param].grid(row=index, column=0, sticky="ew")

    def get_params(self) -> Optional[list[str]]:
        if (val := self.param_frames) is None:
            return None
        return list(val.keys())

    def set_param_values(self, values: dict[str, Any]) -> None:
        keys = self.param_frames.keys()
        if keys != values.keys():
            raise EntryError("Parameter names do not match.")
        for key in keys:
            self.param_frames[key].set_value(values[key])

    def delete_parameter_frames(self) -> None:
        if self.param_frames is not None:
            for frame in self.param_frames.values():
                frame.destroy()
        self.param_frames = dict()

    def rename_entries(self, formula: str) -> str:
        """Renames the entries if this is possible and outputs the new formula."""
        param_rename = dict()
        for old, frame in zip(self.param_frames.keys(), self.param_frames.values()):
            if old != (new := frame.get_entry()):
                param_rename[old] = new
        try:
            formula = rename_parameters(formula, param_rename)  # could fail
        except (RepetitionError, ValueError) as e:
            for frame in self.param_frames.values():
                frame.reset_entry()
            raise EntryError(e.__repr__())

        for old in param_rename.keys():
            new = param_rename[old]
            frame = self.param_frames[old]
            frame.set_name(new)
            self.param_frames[new] = self.param_frames.pop(old)
        return formula

    def reset_parameter_entries(self) -> None:
        for frame in self.param_frames.values():
            frame.reset_entry()
