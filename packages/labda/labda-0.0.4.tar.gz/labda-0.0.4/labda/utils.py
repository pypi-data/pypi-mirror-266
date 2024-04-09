import secrets
from datetime import datetime

import geopandas as gpd
import pandas as pd
import pyproj
from timezonefinder import TimezoneFinder

from .structure.validation.subject import Column


def columns_exists(
    df: pd.DataFrame,
    columns: list[Column | str],
) -> None:
    """
    Checks if the given columns exist in the DataFrame.

    This function iterates over the list of columns and checks if each column exists in the DataFrame.
    If a column does not exist, it raises a ValueError.

    Args:
        df (pd.DataFrame): The DataFrame to check.
        columns (list[str]): A list of column names to check for existence in the DataFrame.

    Raises:
        ValueError: If a column does not exist in df.
    """

    missing_columns = [col for col in columns if col not in df.columns]

    if missing_columns:
        raise ValueError(
            f"The following columns do not exist in the DataFrame: {', '.join(missing_columns)}"
        )


def columns_not_exists(
    df: pd.DataFrame,
    columns: list[Column | str],
    *,
    overwrite: bool = False,
) -> None:
    """
    Checks if the specified columns do not exist in the DataFrame. If 'overwrite' is True,
    existing columns will be dropped. If 'overwrite' is False, an error will be raised for existing columns.

    Args:
        df (pd.DataFrame): The DataFrame to check.
        columns (List[str]): A list of column names to check.
        overwrite (bool, optional): Whether to drop existing columns. Defaults to False.

    Raises:
        ValueError: If 'overwrite' is False and any of the specified columns exist in the DataFrame.

    Returns:
        None
    """
    existing_columns = [col for col in columns if col in df.columns]

    if existing_columns:
        if overwrite:
            df.drop(columns=existing_columns, inplace=True)
        else:
            raise ValueError(
                f"The following columns already exist in the DataFrame: {', '.join(existing_columns)}"
            )


def get_unique_column_name(df: pd.DataFrame) -> str:
    """
    Generates a unique column name that is not present in the given list of columns.

    Args:
        df (pd.DataFrame): The DataFrame to check.

    Returns:
        str: A unique column name.
    """
    hex = 4
    colname = secrets.token_hex(hex)
    while colname in df.columns.tolist():
        colname = secrets.token_hex(hex)

    return colname


def get_sampling_frequency(df: pd.DataFrame) -> float:
    # TODO: Check that index is a datetime index.

    frequencies = df.index.to_series().diff().value_counts()
    dominant_frequency = frequencies.idxmax()

    if len(frequencies) > 1 and frequencies[dominant_frequency] == frequencies.iloc[1]:
        raise ValueError(
            "We are uncertain about the frequency sampling. Please verify the data manually."
        )

    seconds = dominant_frequency.total_seconds()  # type: ignore
    if seconds < 1:
        raise NotImplementedError(
            "Sub-second sampling frequencies are not supported yet."
        )

    return seconds


def convert_to_geodataframe(
    df: pd.DataFrame,
    *,
    crs: str | None = None,
) -> gpd.GeoDataFrame:
    """
    Converts a DataFrame to a GeoDataFrame by creating a geometry column from latitude and longitude columns.

    Args:
        df (pd.DataFrame): The DataFrame to be converted.
        crs (str | None, optional): The coordinate reference system (CRS) of the GeoDataFrame. Defaults to None.

    Returns:
        gpd.GeoDataFrame: The converted GeoDataFrame.
    """

    columns_exists(df, [Column.LATITUDE, Column.LONGITUDE])

    return gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df.longitude, df.latitude), crs=crs
    )  # type: ignore


def convert_to_dataframe(gdf: gpd.GeoDataFrame) -> pd.DataFrame:
    """
    Converts a GeoDataFrame to a DataFrame by extracting the latitude and longitude
    coordinates from the geometry column. The geometry column is dropped in the process.

    Args:
        gdf (gpd.GeoDataFrame): The input GeoDataFrame.

    Returns:
        pd.DataFrame: The converted DataFrame with latitude and longitude columns.
    """
    gdf[Column.LATITUDE] = gdf.geometry.y
    gdf[Column.LONGITUDE] = gdf.geometry.x
    gdf.drop(columns=["geometry"], inplace=True)

    return pd.DataFrame(gdf)


def get_crs(df: pd.DataFrame) -> str:
    """
    Guesses the coordinate reference system (CRS) of a DataFrame containing spatial data. The CRS is estimated using the WGS84 ellipsoid.

    Args:
        df (pd.DataFrame): The DataFrame containing spatial data.

    Returns:
        str: The estimated CRS of the DataFrame.
    """

    gdf = convert_to_geodataframe(df, crs="WGS84")  # type: ignore
    estimated_crs = gdf.geometry.estimate_utm_crs()

    return str(estimated_crs)


def get_timezone(df: pd.DataFrame, sample_size: int = 5) -> str:
    """
    Guesses the dominant timezone based on latitude and longitude coordinates in a DataFrame. The timezone is estimated using the TimezoneFinder package.

    Args:
        df (pd.DataFrame): The DataFrame containing latitude and longitude columns.
        sample_size (int, optional): The number of coordinates to sample for timezone estimation. Defaults to 5.

    Raises:
        ValueError: If there are multiple timezones with the same highest count.

    Returns:
        str: The dominant timezone as a string.
    """

    columns_exists(df, [Column.LATITUDE, Column.LONGITUDE])

    coords = df[df[Column.LATITUDE].notna() & df[Column.LONGITUDE].notna()]
    sample = coords.sample(sample_size)

    tz_finder = TimezoneFinder()
    sample["timezone"] = sample.apply(
        lambda row: tz_finder.timezone_at(lat=row.latitude, lng=row.longitude),  # type: ignore
        axis=1,
    )

    timezones = sample["timezone"].value_counts()
    dominant_timezone = timezones.idxmax()
    if len(timezones) >= 2 and timezones[dominant_timezone] == timezones.iloc[1]:
        raise ValueError(
            "We are uncertain about the timezone. Please verify the data manually."
        )

    return str(dominant_timezone)


def convert_distance_parameter(param: int | float, sampling_frequency: float) -> float:
    """
    Converts a distance parameter to meters.

    This function accepts a distance parameter as an integer or float in meters per minute.
    The function then converts the distance to proper value based on sampling frequency.

    Args:
        distance (int | float): The distance in meters per minute to convert.
        sampling_frequency (float): The sampling frequency in seconds.
    Returns:
        float: The converted distance in meters per minute based on sampling frequency.
    """
    meters = param / (60 / sampling_frequency)
    return meters


def align_datetimes(df: pd.DataFrame, sampling_frequency: float) -> pd.DataFrame:
    df = df.copy()
    # TODO: Add docstring
    diff = get_unique_column_name(df)
    rounded = get_unique_column_name(df)

    df[rounded] = df.index.round(f"{sampling_frequency}s")  # type: ignore
    df[diff] = (df.index - df[rounded]).dt.total_seconds().abs()  # type: ignore
    df = df.sort_values([rounded, diff])
    df.drop(columns=[diff], inplace=True)

    df = df.drop_duplicates(subset=rounded, keep="first")
    df.set_index(rounded, inplace=True, drop=True)
    df.index.name = Column.DATETIME

    return df


def get_crs_units(crs: str) -> str:
    crs = pyproj.CRS(crs)  # type: ignore
    units = crs.axis_info[0].unit_name  # type: ignore

    return units


def change_crs(df: pd.DataFrame, source: str, target: str) -> pd.DataFrame:
    gdf = convert_to_geodataframe(df, crs=source)
    gdf.to_crs(target, inplace=True)
    df = convert_to_dataframe(gdf)

    return df


def change_timezone(df: pd.DataFrame, source: str, target: str) -> pd.DataFrame:
    df = df.copy()
    df.index = df.index.tz_localize(source).tz_convert(target).tz_localize(None)  # type: ignore

    return df


def filter_datetime(
    df: pd.DataFrame,
    start: datetime | None = None,
    end: datetime | None = None,
) -> pd.DataFrame:
    if start and end:
        if end < start:
            raise ValueError("The end time must be after the start time.")

    if start:
        df = df[df.index >= start]

    if end:
        df = df[df.index <= end]

    return df
