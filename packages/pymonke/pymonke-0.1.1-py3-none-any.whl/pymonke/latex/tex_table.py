from dataclasses import dataclass, field
from typing import List


@dataclass(repr=True)
class TexTable:
    r"""Class for generating a LaTeX table. The idea behind this class is to have the ability to
     create a table with multiple tabular environments, in the case where the user wants to have
     multiple tabular environments side by side.
     In the case where one tabular environment is enough, this class is not necessary to generate a LaTeX table.

     Parameters
     ----------
     positioning: str
     Is "htbp" by default and defines the position behavior of the table.
     tabular: List[str]
     Defines a list with strings that represent latex tabulars inside, which contain the data for the tabular
     environments.
     widths: List[float]
     Defines the space relative to the line width of the page that is given for the tabular environments.
     It is a list that should have the same length as the `tabular list.
     spacing: List[float | str]
     Defines the spacing between two tabular environments. It is a list which should be shorter by one
     than the `tabular` list. An element could be a string, which will be inserted verbosely, but in the case
     of a floating point number, it will be inserted as an argument to the `hspace` macro.
     """
    tabular: List[str]
    positioning: str = "htbp"
    widths: List[float] = field(default_factory=list)
    spacing: List[float | str] = field(default_factory=list)

    def save(self, file_path: str, method: str = "w") -> None:
        r"""Saves the LaTeX table to a file specified by `file_path`. The `method` argument is the same as
        for the builtin `open()` function."""
        with open(file_path, method) as file:
            file.write(str(self))

    def __str__(self) -> str:
        content = ""

        if len(self.tabular) == 0:
            raise ValueError("No tabular defined")
        elif len(self.tabular) == 1:
            content = self.tabular[0].__str__()
        else:
            if len(self.tabular) > len(self.widths):
                raise ValueError(r"you need to specify the width of each tabular")
            space: str = ""
            for (index, tab) in enumerate(self.tabular):
                text: str = space
                text += f"\n    \\parbox{{{self.widths[index]}\\linewidth}}{{\n        \\centering\n"
                text += str(tab)
                text += f"\n    }}"
                content += text
                try:
                    s = self.spacing[index]
                    if isinstance(s, float):
                        space = f"\\hspace{{{self.spacing[index]}cm}}"
                    elif isinstance(s, str):
                        space = s
                    else:
                        raise TypeError("the spacing parameter must be a float or a string")
                except IndexError:
                    space = r"\qquad"

        result = f"\\begin{{table}}[{self.positioning}]\n    \\centering\n{content}\n\\end{{table}}"
        return result
