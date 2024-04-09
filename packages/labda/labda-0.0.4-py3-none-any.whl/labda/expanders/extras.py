import pandas as pd

from ..structure.validation.subject import Column
from ..utils import columns_not_exists


def add_timedelta(
    df: pd.DataFrame,
    *,
    name: str = Column.TIMEDELTA,
    overwrite: bool = False,
) -> pd.DataFrame:
    """
    Adds a timedelta column to the DataFrame.

    This function calculates the time difference between each row and the previous row and adds it as a new column to the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to which to add the timedelta column.
        name (str, optional): The name of the new timedelta column. Defaults to "timedelta".
        overwrite (bool, optional): Whether to overwrite the existing timedelta column if it exists. Defaults to False.

    Returns:
        pd.DataFrame: The DataFrame with the added timedelta column.
    """

    columns_not_exists(df, [name], overwrite=overwrite)

    df = df.copy()

    df[name] = df.index.diff()  # type: ignore

    return df
