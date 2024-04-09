from datetime import timedelta
from typing import Any

import pandas as pd

from ..structure.validation.subject import SCHEMA

# TODO: Need to be tested, probably refactored!


def get_wear_time(df: pd.DataFrame, sampling_frequency: float) -> pd.Series:
    series = df.groupby(pd.Grouper(level="datetime", freq="D"))["wear"].sum()
    series = series.rename("wear_time")
    series = series.apply(lambda x: timedelta(seconds=(x * sampling_frequency)))
    return series


def get_wear_days(
    df: pd.DataFrame, sampling_frequency: float, min_time: timedelta
) -> pd.DataFrame:
    days = get_wear_time(df, sampling_frequency).to_frame()

    days["valid"] = days["wear_time"] >= min_time
    days["day"] = days.index.day_of_week  # type: ignore
    days["day_type"] = days["day"].apply(lambda x: "weekend" if x > 4 else "weekday")

    return days.drop(columns=["day"])


def get_wear_validity(
    df: pd.DataFrame,
    sampling_frequency: float,
    min_time: timedelta,
    weekday: int = 0,
    weekend: int = 0,
) -> tuple[dict[str, Any], pd.DataFrame]:
    if weekday == 0 and weekend == 0:
        raise ValueError(
            "Parameters weekday and weekend cannot both be 0. Please set at least one of them to a positive number of days."
        )

    days = get_wear_days(df, sampling_frequency, min_time)
    day_types = days.groupby("day_type")["valid"].value_counts().reset_index()

    weekday_count = day_types.loc[
        (day_types["day_type"] == "weekday") & (day_types["valid"] == True)
    ]
    if not weekday_count.empty:
        weekday_count = weekday_count["count"].values[0]
    else:
        weekday_count = 0

    weekend_count = day_types.loc[
        (day_types["day_type"] == "weekend") & (day_types["valid"] == True)
    ]
    if not weekend_count.empty:
        weekend_count = weekend_count["count"].values[0]
    else:
        weekend_count = 0

    weekday_valid = True if weekday_count >= weekday else False
    weekend_valid = True if weekend_count >= weekend else False
    valid = weekday_valid and weekend_valid

    return {
        "weekday": {"valid": weekday_valid, "count": weekday_count},
        "weekend": {"valid": weekend_valid, "count": weekend_count},
        "valid": valid,
    }, days
