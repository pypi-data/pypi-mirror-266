from customtkinter import CTkComboBox

from typing import Callable, Any

from ..misc import get_root, get_meta


class FitComboBox(CTkComboBox):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs, values=["Add Fit"], command=self.on_selection)
        self.bind("<Return>", self.add_or_rename)

        self.selection_bindings: list[Callable[[], None]] = []
        self.return_bindings: list[Callable[[], None]] = []
        self.delete_bindings: list[Callable[[], None]] = []

        self.selected: str = "Add Fit"

    def add_or_rename(self, _: Any = None) -> None:
        if (fits := get_meta(self).get("fits")) is None:
            get_meta(self)["fits"] = fits = dict()

        fit_name: str = self.get()
        old: list[str] = self.cget("values")
        if fit_name in old:
            return
        if self.selected == "Add Fit":  # Add
            if fit_name == "Add Fit":
                return
            old.insert(-2, fit_name)
            self.configure(values=old)
            self.set(fit_name)
            fits[fit_name] = dict()
            self.selected = fit_name
        else:  # Rename or delete
            if fit_name == "":
                self.delete_option(self.selected)
            else:
                for i, name in enumerate(old):
                    if name == self.selected:
                        old[i] = fit_name
                fits[fit_name] = fits.pop(self.selected)
                self.selected = fit_name
                self.configure(values=old)
        # self.change_meta_of_plotting_arguments()
        for binding in self.return_bindings:
            binding()

    def delete_option(self, option_to_delete: str) -> None:
        options: list[str] = self.cget("values")
        if option_to_delete not in options:
            raise ValueError(f"Invalid option: {option_to_delete}. Cannot delete option because it does not exist.")
        get_root(self).meta["fits"].pop(option_to_delete)
        options.remove(option_to_delete)
        self.set("Add Fit")
        self.selected = "Add Fit"
        self.configure(values=options)
        for binding in self.delete_bindings:
            binding()

    def on_selection(self, _: Any = None) -> None:
        self.selected = self.get()
        for binding in self.selection_bindings:
            binding()
        # self.change_meta_of_plotting_arguments()
