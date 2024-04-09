from pandas import DataFrame

from typing import List, Sequence, Any, Iterable

from uncertainties.core import Variable, AffineScalarFunc
from uncertainties import ufloat


def get_error_column_name(data: DataFrame, column: str, error_marker: List[str] | None = None) -> str | None:
    """Get the columns name that is the uncertainty of the column argument. return None if not found.
    parameters
    ----------
    data: DataFrame
    The dataframe to analyze.
    column: str
    The name of the column which represents a series of values that have an uncertainty.
    error_marker: List[str]
    A list of words that indicate that a column represents a series of uncertainties.
    """
    columns = list(data.columns)
    if column not in columns:
        raise ValueError("column not in DataFrame")

    if error_marker is None:
        error_marker = ["error", "err", "fehler", "Error", "Err", "Fehler"]

    error_separator = ["_", "-", " ", ""]
    result: str | None = None
    for marker in error_marker:
        for separator in error_separator:
            if f"{column}{separator}{marker}" in columns:
                if result is None:
                    result = f"{column}{separator}{marker}"
                else:
                    text = f"""Error in DataFrame for the column {column} could not be determined because 
                    of ambivalence. Error marker are {error_marker}"""
                    raise ValueError(text)
    return result


def has_uncertainty(data: Iterable) -> bool:
    """checks if the data sequence has an uncertainty attached to it."""
    for element in data:
        if not isinstance(element, (Variable, AffineScalarFunc)):
            return False
    return True


def separate_uncertainties(dataframe: DataFrame, inplace: bool = False, error_name: str = "error") -> DataFrame:
    if inplace:
        new_dataframe = dataframe
    else:
        new_dataframe = dataframe.copy()

    for column in dataframe.columns:
        if has_uncertainty(new_dataframe[column]):
            data = new_dataframe[column]
            new_dataframe[f"{column} {error_name}"] = [x.std_dev for x in data]
            new_dataframe[column] = [x.nominal_value for x in data]

    return new_dataframe


def join_uncertainties(dataframe: DataFrame, inplace: bool = False,
                       error_marker: List[str] | None = None) -> DataFrame:
    """If a Series has uncertainties in another DataFrame, it finds them and  joins
    into one Series with the Variable type of the uncertainties package."""
    if inplace:
        new_dataframe = dataframe
    else:
        new_dataframe = dataframe.copy()

    error_columns: list[str] = []
    for column in new_dataframe.columns:
        if (error_name := get_error_column_name(new_dataframe, column, error_marker)) is not None:
            error_columns.append(error_name)
            new_dataframe[column] = [ufloat(x, err) for x, err in
                                     zip(new_dataframe[column], new_dataframe[error_name])]

    new_dataframe.drop(error_columns, axis=1, inplace=True)
    return new_dataframe
