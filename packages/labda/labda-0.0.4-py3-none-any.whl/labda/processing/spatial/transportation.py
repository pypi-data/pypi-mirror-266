from typing import Any

import pandas as pd
from pandas.core.groupby import DataFrameGroupBy

from ...expanders.spatial import add_speed
from ...structure.validation.subject import Column
from ...utils import columns_exists, columns_not_exists, get_unique_column_name

# TODO: Add something, so even pause has a mode.
# TODO: Option: pause_mode = True/False, before, after, mixed?


def _set_trip_mode(df: pd.DataFrame, name: str):
    modes = df[name].value_counts()
    dominant_mode = modes.idxmax()
    df[name] = dominant_mode


def _get_partial_trips(df: pd.DataFrame) -> DataFrameGroupBy:
    helper_column = get_unique_column_name(df)
    df.loc[~df["trip_status"].isin(["stationary", "pause"]), helper_column] = (
        df["trip_status"] == "start"
    ).cumsum()

    return df.groupby(["trip_id", helper_column])


def _detect_partial_transport(
    df: pd.DataFrame,
    on: Column | str,
    cut_points: dict[str, Any],
    window: int | None = None,
    name: str = "trip_mode",
) -> pd.DataFrame:
    if window:
        df[on] = df[on].rolling(window=window, min_periods=1).mean()

    # Extract max values from cut_points
    bins = [-float("inf")]
    bins += [cp["max"] for cp in cut_points["cut_points"]]

    # Extract names from cut_points
    labels = [cp["name"] for cp in cut_points["cut_points"]]

    # Apply cut points
    df[name] = pd.cut(df[on], bins=bins, labels=labels)

    _set_trip_mode(df, name)

    return df


def detect_transportation(
    df: pd.DataFrame,
    crs: str,
    cut_points: dict[str, Any],
    *,
    window: int | None = None,
    name: str = Column.TRIP_MODE,
    overwrite: bool = False,
) -> pd.DataFrame:
    columns_not_exists(df, [name], overwrite=overwrite)

    required_column = cut_points["required_data"]
    columns_exists(df, [Column.TRIP_ID, Column.TRIP_STATUS, required_column])

    temp_df = df.copy()

    if required_column == Column.SPEED:
        temp_df = add_speed(temp_df, crs=crs, overwrite=True)

    partials = _get_partial_trips(temp_df)
    partials = partials.apply(
        lambda x: _detect_partial_transport(
            x, required_column, cut_points, window, name
        ),
        include_groups=False,
    ).reset_index(level=[0, 1])

    df = df.merge(partials[name], on=Column.DATETIME, how="left")

    return df
