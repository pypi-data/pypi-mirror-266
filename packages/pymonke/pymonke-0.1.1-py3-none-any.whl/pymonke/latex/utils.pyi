from pandas import DataFrame


def transform_dataframe_to_latex_ready(data: DataFrame, **kwargs) -> DataFrame:
    r"""Iterates through the column names and tries to find the corresponding error column.
    If it is found, both columns will be put together into a new column with the numbers separated by a plusminus
    sign. Other numbers in the DataFrame will be put inside the tablenum macro for proper alignment inside the
    table.

    Parameters
    ----------
    data: DataFrame
    Data to be transformed into other data that can be made into a string to work with LaTeX tables.

    Keyword Parameters
    ------------------
    error_marker: List[str], optional
    Defines a list of all string suffixes that mark a column of uncertainties. The default value
    is ["err", "error", "fehler", "Err", "Error", "Fehler"].
    columns: Dict[str, str], optional
    If a Key corresponds to a column of the data, that column will be renamed to the given value.
    ignore_rest: bool, optional
    If set to true, every column of the data that is not a key in the `columns` keyword argument will
    be dropped in the resulting DataFrame. The default value is `False`.
    is_table_num: bool, optional
    If false, numbers will not be inserted in the tablenum macro but the num macro instead. Default value is `True`.
    siunitx_column_option: Dict[str, str], optional
    For every column that is a key in the given dictionary, the value is inserted as an option for the tablenum
    macro.
    """
    ...
