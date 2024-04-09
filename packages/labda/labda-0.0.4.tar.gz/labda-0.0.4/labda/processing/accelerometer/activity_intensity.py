import copy
from typing import Any

import pandas as pd

from ...structure.validation.subject import Column
from ...utils import columns_exists, columns_not_exists


def scale_cut_points(
    cut_points: dict[str, Any], sampling_frequency: float
) -> dict[str, Any]:
    cut_points = copy.deepcopy(cut_points)
    from_sf = cut_points["sampling_frequency"]
    for cp in cut_points["cut_points"]:
        if cp.get("max") is not None:
            cp["max"] = cp["max"] / (from_sf / sampling_frequency)

    return cut_points


def apply_cut_points(
    df: pd.DataFrame, on: Column | str, cut_points: dict[str, Any], name: str
):
    # Extract min and max values from cut_points
    bins = [-float("inf")]
    bins += [cp["max"] for cp in cut_points["cut_points"]]

    # Extract names from cut_points
    labels = [cp["name"] for cp in cut_points["cut_points"]]

    # Apply cut points
    df[name] = pd.cut(df[on], bins=bins, labels=labels)


def detect_activity_intensity(
    df: pd.DataFrame,
    cut_points: dict[str, Any],
    sampling_frequency: float,
    *,
    name: str = Column.ACTIVITY_INTENSITY,
    overwrite: bool = False,
):
    columns_not_exists(df, [name], overwrite=overwrite)

    required_column = cut_points["required_data"]
    columns_exists(df, [required_column])

    df = df.copy()

    # Check sampling frequency if needed scale cut points
    if cut_points["sampling_frequency"] != sampling_frequency:
        cut_points = scale_cut_points(cut_points, sampling_frequency)

    apply_cut_points(df, required_column, cut_points, name)

    return df
