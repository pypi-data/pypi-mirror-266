import numpy as np
import pandas as pd

from ..structure.validation.subject import Column
from ..utils import (
    columns_exists,
    columns_not_exists,
    convert_to_geodataframe,
    get_crs,
    get_crs_units,
    get_unique_column_name,
)
from .extras import add_timedelta

__all__ = [
    "add_speed",
    "add_distance",
    "add_acceleration",
    "add_direction",
    "add_elevation",
    # "add_weather",
    # "add_address",
]


def add_speed(
    df: pd.DataFrame,
    *,
    crs: str | None = None,
    name: str = Column.SPEED,
    overwrite: bool = False,
) -> pd.DataFrame:
    """
    Adds a speed column to the DataFrame by calculating the speed based on the distance and time.
    Units are based on the CRS. If CRS is not specified, the CRS will be guessed based on the coordinates (WGS84 by default).

    Args:
        df (pd.DataFrame): The input DataFrame.
        crs (str | None, optional): The coordinate reference system. Defaults to None.
        name (str, optional): The name of the speed dataframe.Column. Defaults to "speed".
        overwrite (bool, optional): Whether to overwrite the existing speed column if it already exists.
            Defaults to False.

    Returns:
        pd.DataFrame: The DataFrame with the speed column added.

    Raises:
        ValueError: If the speed column already exists in the DataFrame and overwrite is set to False.
    """

    columns_not_exists(df, [name], overwrite=overwrite)

    df = df.copy()

    timedelta_colname = get_unique_column_name(df)
    df = add_timedelta(df, name=timedelta_colname)

    distance_colname = get_unique_column_name(df)
    df = add_distance(df, crs=crs, name=distance_colname)

    df[name] = df[distance_colname] / df[timedelta_colname].dt.total_seconds()

    # TODO: This is temporary fix for changing m/s to km/h for now.
    if crs:
        units = get_crs_units(crs)

        if units == "metre":
            df[name] = df[name] * 3.6

    return df.drop(columns=[timedelta_colname, distance_colname])


def add_distance(
    df: pd.DataFrame,
    *,
    crs: str | None = None,
    name: str = Column.DISTANCE,
    overwrite: bool = False,
) -> pd.DataFrame:
    """
    Adds a column to the DataFrame with the distance between consecutive points.
    Units are based on the CRS. If CRS is not specified, the CRS will be guessed based on the coordinates (WGS84 by default).

    Args:
        df (pd.DataFrame): The input DataFrame.
        crs (str | None, optional): The coordinate reference system of the DataFrame. Defaults to None.
        name (str, optional): The name of the new dataframe.Column. Defaults to "distance".
        overwrite (bool, optional): Whether to overwrite the existing column with the same name. Defaults to False.

    Returns:
        pd.DataFrame: The DataFrame with the added distance dataframe.Column.

    Raises:
        ValueError: If the column with the specified name already exists in the DataFrame and overwrite is False.
    """

    columns_exists(df, [Column.LATITUDE, Column.LONGITUDE])
    columns_not_exists(df, [name], overwrite=overwrite)

    df = df.copy()
    gdf = convert_to_geodataframe(df, crs=crs)
    if gdf.crs is None:
        crs = get_crs(gdf)
        gdf = gdf.set_crs(crs)

    df[name] = gdf.distance(gdf.shift(1))  # type: ignore

    return df


def add_acceleration(
    df: pd.DataFrame,
    *,
    crs: str | None = None,
    name: str = Column.ACCELERATION,
    overwrite: bool = False,
) -> pd.DataFrame:
    """
    Adds a column to the DataFrame with the acceleration between consecutive points.
    Acceleration is calculated based on the change in speed over time.
    Units are based on the CRS. If CRS is not specified, the CRS will be guessed based on the coordinates (WGS84 by default).

    Args:
        df (pd.DataFrame): The input DataFrame.
        crs (str | None, optional): The coordinate reference system of the DataFrame. Defaults to None.
        name (str, optional): The name of the new dataframe.Column. Defaults to "acceleration".
        overwrite (bool, optional): Whether to overwrite the existing column with the same name. Defaults to False.

    Returns:
        pd.DataFrame: The DataFrame with the added acceleration dataframe.Column.

    Raises:
        ValueError: If the column with the specified name already exists in the DataFrame and overwrite is False.
    """

    # TODO: Needs to be tested.
    columns_not_exists(df, [name], overwrite=overwrite)

    df = df.copy()

    speed_colname = get_unique_column_name(df)
    df = add_speed(df, crs=crs, name=speed_colname)

    timedelta_colname = get_unique_column_name(df)
    df = add_timedelta(df, name=timedelta_colname)

    df[name] = (df[speed_colname] - df[speed_colname].shift()) / df[
        timedelta_colname
    ].dt.total_seconds()

    return df.drop(columns=[speed_colname, timedelta_colname])


def add_direction(
    df: pd.DataFrame,
    *,
    name: str = Column.DIRECTION,
    overwrite: bool = False,
) -> pd.DataFrame:
    """
    Adds a column to the DataFrame with the direction between consecutive points.
    Direction is calculated based on the change in longitude and latitude.

    Args:
        df (pd.DataFrame): The input DataFrame.
        name (str, optional): The name of the new dataframe.Column. Defaults to "direction".
        overwrite (bool, optional): Whether to overwrite the existing column with the same name. Defaults to False.

    Returns:
        pd.DataFrame: The DataFrame with the added direction dataframe.Column.

    Raises:
        ValueError: If the column with the specified name already exists in the DataFrame and overwrite is False.
    """

    # TODO: Needs to be tested.
    columns_exists(df, [Column.LATITUDE, Column.LONGITUDE])
    columns_not_exists(df, [name], overwrite=overwrite)

    df = df.copy()

    # Convert to radians
    lon1, lat1 = np.radians(df[Column.LONGITUDE]), np.radians(df[Column.LATITUDE])
    lon2, lat2 = (
        np.radians(df[Column.LONGITUDE].shift()),
        np.radians(df[Column.LATITUDE].shift()),
    )

    dlon = lon2 - lon1

    x = np.cos(lat2) * np.sin(dlon)
    y = np.cos(lat1) * np.sin(lat2) - np.sin(lat1) * np.cos(lat2) * np.cos(dlon)

    direction = np.arctan2(x, y)
    direction = np.degrees(direction)
    direction = (direction + 360) % 360

    df[name] = direction

    return df


def add_elevation(
    df: pd.DataFrame,
    *,
    name: str = Column.ELEVATION,
    overwrite: bool = False,
) -> pd.DataFrame:
    # TODO: Add elevation.

    columns_not_exists(df, [name], overwrite=overwrite)

    raise NotImplementedError("This method needs to be implemented.")


# def add_weather(
#     df: pd.DataFrame,
#     *,
#     name: str = "weather",
#     overwrite: bool = False,
# ) -> pd.DataFrame:
#     # TODO: https://open-meteo.com/en/docs/historical-weather-api/
#     # TODO: Add weather.

#     if not overwrite:
#         check_columns_existence(df, [name], exists=False)

#     raise NotImplementedError("This method needs to be implemented.")


# def add_address(
#     df: pd.DataFrame,
#     *,
#     name: str = "address",
#     overwrite: bool = False,
# ) -> pd.DataFrame:
#     # TODO: Add address.

#     if not overwrite:
#         check_columns_existence(df, [name], exists=False)

#     raise NotImplementedError("This method needs to be implemented.")
