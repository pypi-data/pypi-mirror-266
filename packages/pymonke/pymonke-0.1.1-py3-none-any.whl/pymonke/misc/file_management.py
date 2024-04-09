import numpy as np
import pandas as pd
from pandas import DataFrame

from typing import List, Any


def get_file_type(filename: str) -> str:
    return filename.split('.')[-1]


def read_txt_into_dataframe(file: str, skiprows: int = 1, **args: Any) -> DataFrame:
    columns: List[str]
    with open(file, 'r') as f:
        if (delim := args.get("delimiter")) is None:
            delim = " "
        columns = f.readline().replace(delim, " ").replace("\t", " ").replace("\n", "").split(" ")
    data = np.loadtxt(file, skiprows=skiprows, **args)
    return DataFrame(data=data, columns=columns)


def read_data_into_dataframe(file: str, **args: Any) -> DataFrame:
    """tries to Convert the file into a DataFrame"""
    file_type = get_file_type(file)
    if file_type == "csv":
        return pd.read_csv(file, **args)
    elif file_type == "txt":
        return read_txt_into_dataframe(file, **args)
    else:
        raise ValueError(f"File type {file_type} not supported")
