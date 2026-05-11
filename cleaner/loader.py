"""
loader.py
---------
Handles loading the raw CSV file into a pandas DataFrame.

Keeping loading logic separate from cleaning logic means:
  - If the file format changes, only this module needs updating.
  - The cleaner can be tested with any DataFrame, not just from files.
"""

import pandas as pd

from .exceptions import FileNotFoundError, EmptyFileError


def load_csv(file_path: str) -> pd.DataFrame:
    """
    Load a CSV file into a DataFrame with basic validation.

    Parameters
    ----------
    file_path : str
        Absolute or relative path to the CSV file to load.

    Returns
    -------
    pd.DataFrame
        The raw file contents as a DataFrame.

    Raises
    ------
    FileNotFoundError
        If the file does not exist at the given path.
    EmptyFileError
        If the file exists but contains no data rows.
    """
    try:
        df = pd.read_csv(file_path, dtype=str)  # Read everything as strings first
    except FileNotFoundError:
        raise FileNotFoundError(file_path)
    except pd.errors.EmptyDataError:
        raise EmptyFileError(file_path)

    if df.empty:
        raise EmptyFileError(file_path)

    return df
