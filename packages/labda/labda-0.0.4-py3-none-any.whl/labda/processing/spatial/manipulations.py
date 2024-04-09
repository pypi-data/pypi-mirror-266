from collections import deque
from datetime import timedelta

import pandas as pd

from ...expanders import add_speed
from ...utils import (
    columns_exists,
    columns_not_exists,
    convert_to_geodataframe,
    get_crs,
    get_unique_column_name,
)


def stop_splitter(
    df: pd.DataFrame,
    *,
    max_radius: int | float,
    min_duration: timedelta,
    crs: str | None = None,
    name: str = "stop",
    overwrite: bool = False,
) -> pd.DataFrame:
    """
    Splits a DataFrame into stop segments based on a maximum radius and minimum duration.

    Args:
        df (pd.DataFrame): The input DataFrame.
        max_radius (int | float): The maximum radius within which points are considered part of a stop segment.
        min_duration (timedelta): The minimum duration required for a stop segment.
        crs (str | None, optional): The coordinate reference system of the input DataFrame. Defaults to None.
        name (str, optional): The name of the column to be added to the DataFrame to indicate stop segments. Defaults to "stop".

    Returns:
        pd.DataFrame: The modified DataFrame with the added stop column. The stop column is True for stop segments and False otherwise.

    Raises:
        ValueError: If the specified column name already exists in the DataFrame and overwrite is set to False.
    """

    columns_not_exists(df, [name], overwrite=overwrite)

    # TODO: How to handle NA values, maybe just filter to have only valid points (with coordinates).
    df = df.copy()
    df[name] = False

    gdf = convert_to_geodataframe(df, crs=crs)
    if gdf.crs is None:
        crs = get_crs(gdf)
        gdf = gdf.set_crs(crs)

    buffer = deque()
    for dt in gdf.index:
        buffer.append(dt)
        if dt - buffer[0] >= min_duration:
            selected_rows = gdf.loc[buffer[0] : dt]
            centroid = selected_rows.geometry.unary_union.centroid

            for row in selected_rows.geometry:
                distance = centroid.distance(row)
                if distance > max_radius:
                    break
            else:
                df.loc[selected_rows.index, name] = True

            buffer.popleft()

    return df.astype({name: "boolean"})


def min_distance_filter(
    df: pd.DataFrame,
    *,
    min_distance: int | float,
    crs: str | None = None,
    name: str = "min_distance",
    overwrite: bool = False,
) -> pd.DataFrame:
    """
    Filters a DataFrame based on the minimum distance between consecutive points.

    Args:
        df (pd.DataFrame): The input DataFrame.
        min_distance (int | float): The minimum distance threshold.
        crs (str | None, optional): The coordinate reference system of the DataFrame. Defaults to None.
        name (str, optional): The name of the new column to be added. Defaults to "min_distance".
        overwrite (bool, optional): Whether to overwrite the existing column with the same name. Defaults to False.

    Returns:
        pd.DataFrame: The filtered DataFrame with an additional column indicating whether each point meets the minimum distance requirement. The column is True if the point meets the requirement and False otherwise.

    Raises:
        ValueError: If the specified column name already exists in the DataFrame and overwrite is set to False.
    """

    columns_not_exists(df, [name], overwrite=overwrite)

    gdf = convert_to_geodataframe(df, crs=crs)
    if gdf.crs is None:
        crs = get_crs(gdf)
        gdf = gdf.set_crs(crs)

    keep_pts = [gdf.index[0]]  # Keep first point, always.
    prev_pt = gdf.geometry.iloc[0]

    for idx, pt in gdf.geometry.items():
        dist = pt.distance(prev_pt)
        if dist >= min_distance:
            keep_pts.append(idx)
            prev_pt = pt

    keep_pts.append(gdf.index[-1])

    df = df.copy()
    df[name] = False
    df.loc[keep_pts, name] = True

    return df.astype({name: "boolean"})


def max_speed_filter(
    df: pd.DataFrame,
    *,
    max_speed: int | float | None = None,
    crs: str | None = None,
    name: str = "max_speed",
    overwrite: bool = False,
) -> pd.DataFrame:
    """
    Filters the DataFrame based on the maximum speed value.

    Args:
        df (pd.DataFrame): The input DataFrame.
        max_speed (int | float): The maximum speed value to filter by.
        crs (str | None, optional): The coordinate reference system. Defaults to None.
        name (str, optional): The name of the new column to store the filter result. Defaults to "max_speed".
        overwrite (bool, optional): Whether to overwrite the existing column with the same name. Defaults to False.

    Returns:
        pd.DataFrame: The filtered DataFrame with the new column added. The column is True if the point meets the requirement and False otherwise.

    Raises:
        ValueError: If the specified column name already exists in the DataFrame and overwrite is set to False.
    """
    columns_not_exists(df, [name], overwrite=overwrite)

    if max_speed is None:
        # TODO: Should be 95th percentile of the speed.
        raise NotImplementedError("max_speed=None is not yet implemented.")

    gdf = convert_to_geodataframe(df, crs=crs)
    if gdf.crs is None:
        crs = get_crs(gdf)
        gdf = gdf.set_crs(crs)

    prev = gdf.iloc[0]
    prev = (prev.name, prev.geometry)

    # TODO: The invalid point logic is working that if the point is invalid, and the next point is the same, then it should be skipped as well.
    # invalid_pt = None

    keep_idx = [prev[0]]  # Keep first point, always.

    for idx, pt in gdf.geometry.iloc[1:].items():
        dist = pt.distance(prev[1])

        # if invalid_pt and invalid_pt.equals(pt):
        #     continue

        delta_dt = (idx - prev[0]).total_seconds()  # type: ignore
        speed = (dist / delta_dt) * 3.6

        if speed <= max_speed:
            keep_idx.append(idx)
            prev = (idx, pt)
        #     invalid_pt = None
        # else:
        #     invalid_pt = pt

    keep_idx.append(gdf.index[-1])

    df = df.copy()
    df[name] = False
    df.loc[keep_idx, name] = True

    return df.astype({name: "boolean"})
