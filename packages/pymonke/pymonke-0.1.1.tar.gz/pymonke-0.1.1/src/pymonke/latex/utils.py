import pandas as pd

from uncertainties import ufloat
from typing import Any

from ..misc.dataframe import get_error_column_name


def transform_dataframe_to_latex_ready(data: pd.DataFrame, **kwargs: Any) -> pd.DataFrame:
    # initialize all keyword arguments
    if kwargs.get("error_marker") is None:
        kwargs["error_marker"] = ["err", "error", "fehler", "Err", "Error", "Fehler"]
    else:
        list(kwargs["error_marker"])
    if kwargs.get("columns") is None:
        kwargs["columns"] = {}
    else:
        dict(kwargs["columns"])
    if kwargs.get("ignore_rest") is None:
        kwargs["ignore_rest"] = False
    if not isinstance(kwargs["ignore_rest"], bool):
        raise TypeError("ignore_rest must be boolean")
    if kwargs.get("is_table_num") is None:
        kwargs["is_table_num"] = True
    if not isinstance(kwargs["is_table_num"], bool):
        raise TypeError("is_table must be a boolean")
    if kwargs.get("siunitx_column_option") is None:
        kwargs["siunitx_column_option"] = {}
    else:
        dict(kwargs["siunitx_column_option"])

    new_dataframe = data.copy()  # new dataframe for end result
    new_dataframe = new_dataframe.apply(lambda x: replace_ufloat_with_latex_macro(x, **kwargs), axis=0)

    # look for columns with errors
    for column in data.columns:
        error = get_error_column_name(data, column, kwargs["error_marker"])
        if error is None:
            continue
        num_data = data[column]
        error_data = data[error]
        new_data = []
        option: str | None = kwargs["siunitx_column_option"].get(column)
        for x, err in zip(num_data, error_data):
            num = "{:S}".format(ufloat(x, err))
            # if kwargs["is_table_num"]:
            #     new_data.append(NumWithError(x, err).display_table_separate(option))
            # else:
            #     new_data.append(NumWithError(x, err).display_separate(option))
            new_data.append(num_in_siunitx(num, kwargs["is_table_num"], option))
        new_dataframe[column] = new_data
        new_dataframe.drop(error, axis=1, inplace=True)


    if kwargs["ignore_rest"]:
        columns = list(new_dataframe.columns)
        columns_to_ignore = [c for c in columns if c not in kwargs["columns"]]
        new_dataframe.drop(columns=columns_to_ignore, inplace=True)

    for col in list(new_dataframe.columns):
        option = kwargs["siunitx_column_option"].get(col)
        is_table_num: bool = kwargs["is_table_num"]
        new_dataframe[col] = [__display_num_value(i, option, is_table_num) if isinstance(i, (int, float)) else i
                              for i in new_dataframe[col]]

    new_dataframe.rename(columns=kwargs["columns"], inplace=True)

    return new_dataframe


def num_in_siunitx(num: str, is_table_num: bool = False, option: str | None = None) -> str:
    """Wraps number string insided \num or \tablenum macro depending on is_table_num boolean.
    option is another string put in []  as a macro option. """
    if is_table_num:
        text = "tablenum"
    else:
        text = "num"
    if option is None:
        option = ""
    else:
        option = f"[{option}]"

    return f"\\{text}{option}{{{num}}}"


def replace_ufloat_with_latex_macro(x: pd.Series, **kwargs: Any) -> pd.Series:
    def func(i: Any) -> Any:
        try:
            val = "{:S}".format(i)
            return num_in_siunitx(val, kwargs.get("is_table_num") or False,
                                  kwargs["siunitx_column_option"].get(x.name))
        except:
            return i

    return x.apply(func)


def __display_num_value(x: int | float, option: str | None = None, is_table_num: bool = True) -> str | None:
    """takes a number and formats it to use with the siunitx package. Returns None if the value is not a number
    Example
    -------
    __display_num_value(2.3, sinuitx_option="round-mode=figures") -> \tablenum[round-mode=figures]{2.3}"""
    if str(x) == "nan":
        return None
    if option != "" and option is not None:
        option = f"[{option}]"
    else:
        option = ""

    macro = "tablenum"
    if not is_table_num:
        macro = "num"
    return f"\\{macro}{option}{{{x}}}"


if __name__ == "__main__":
    print(__display_num_value(2.23, option="round-mode=figures", is_table_num=False))
