from datetime import timedelta
from operator import ge
from xml import dom

import numpy as np
import pandas as pd
from requests import get

from ...expanders import add_distance
from ...structure.validation.subject import SCHEMA
from ...utils import (
    columns_exists,
    columns_not_exists,
    convert_distance_parameter,
    get_unique_column_name,
)
from ..manipulations import gap_splitter
from .manipulations import max_speed_filter, min_distance_filter, stop_splitter

# TODO: Fix docstring.
# TODO: Test params.
# TODO: Change column names to constants (Column).


def get_trips(
    df: pd.DataFrame,
    *,
    crs: str,
    stop_radius: int | float,
    stop_duration: timedelta,
) -> pd.DataFrame:
    """
    Processes the given DataFrame to identify and label trips based on stops.

    This function applies a stop splitter to the DataFrame based on the given maximum radius and minimum stop duration.
    It then assigns a unique ID to each stop and labels the trip status as either 'stationary' or 'transport'.

    Args:
        df (pd.DataFrame): The input DataFrame to process.
        crs (str): The coordinate reference system to use when processing the DataFrame. The latitude and longitude columns must be in this CRS, otherwise the results will be incorrect.
        max_radius (int | float): The maximum radius to use when splitting stops.
        stop_duration (timedelta): The minimum duration to consider a stop.

    Returns:
        pd.DataFrame: The processed DataFrame with added 'stop_id' and 'trip_status' columns.
    """
    # Returns a new DataFrame with a 'stop' column.
    df = stop_splitter(
        df,
        max_radius=stop_radius,
        min_duration=stop_duration,
        crs=crs,
    )

    # Unique ID for each stop.
    df["stop_id"] = (df["stop"].diff() != 0).cumsum()

    # Set the trip status to 'stationary' if the point is a stop, otherwise 'transport'.
    df["trip_status"] = np.where(df["stop"], "stationary", "transport")

    # Creating category column and setting the categories.
    # FIXME: Import categories from Subject SCHEMA.
    # TODO: Maybe move all the setting of categories to a separate function and as initialisation (start of the detect_trips function).
    categories = [
        "start",
        "end",
        "start-end",
        "transport",
        "pause",
        "stationary",
    ]
    df["trip_status"] = pd.Categorical(
        df["trip_status"], categories=categories, ordered=False
    )

    return df.astype({"stop_id": "UInt16"})


def get_pauses(
    df: pd.DataFrame,
    *,
    crs: str,
    pause_radius: int | float,
    pause_duration: timedelta,
) -> pd.Series:
    """
    Identifies and labels pauses within trips in the given DataFrame.

    This function applies a stop splitter to the DataFrame based on the given maximum radius and minimum pause duration.
    It then assigns a unique ID to each pause and labels the pause status as either 'pause' or 'transport'.

    Args:
        df (pd.DataFrame): The input DataFrame to process.
        crs (str): The coordinate reference system to use when processing the DataFrame. The latitude and longitude columns must be in this CRS, otherwise the results will be incorrect.
        max_radius (int | float): The maximum radius to use when splitting pauses.
        pause_duration (timedelta): The minimum duration to consider a pause.

    Returns:
        pd.Series: A series containing the pause status for each pause point.
    """
    # Select only the rows that are not stops.
    partials = df[~df["stop"]].groupby("stop_id", as_index=False)

    # Returns a new DataFrame with a 'pause' column.
    partials = partials.apply(
        lambda x: stop_splitter(
            x,
            max_radius=pause_radius,
            min_duration=pause_duration,
            crs=crs,
            name="pause",
        )
    ).reset_index(level=0, drop=True)

    # If there are no pauses, return an empty Series.
    if partials.empty:
        return pd.Series(name="partial_status")

    # Unique ID for each pause.
    partials["partial_id"] = (partials["pause"].diff() != 0).cumsum().astype("UInt16")

    # Set the pause status to 'pause' if the point is a pause, otherwise 'transport'.
    partials["partial_status"] = np.where(partials["pause"], "pause", "transport")

    # Select only the rows that are pauses.
    pauses = partials[partials["pause"] == True]

    # Return the pause status for merging (combining).
    return pauses["partial_status"]


def add_boundaries(
    df: pd.DataFrame,
    *,
    id_col: str,
    status_col: str,
    extremities: bool,
) -> None:
    """
    Adds 'start' and 'end' statuses to the trip segments in the DataFrame.

    Args:
        df (pd.DataFrame): The input DataFrame to process.
        id_col (str): The name of the column in df that contains the unique ID for each trip.
        status_col (str): The name of the column in df that contains the trip status.
        extremities (bool): If True, the function will add 'start' and 'end' statuses to the first and last trips, respectively.

    Returns:
        None. The function modifies df in-place.
    """

    # If 'transport' is at the start or end of the DataFrame, change it to 'start' or 'end' respectively.
    if extremities:
        if df.iloc[0][status_col] == "transport":
            df.iloc[0, df.columns.get_loc(status_col)] = "start"
        if df.iloc[-1][status_col] == "transport":
            df.iloc[-1, df.columns.get_loc(status_col)] = "end"

    # Create a temporary DataFrame that shifts the trip status by 1 row forward and backward.
    temp_df_prev = df.shift(1)
    temp_df_next = df.shift(-1)

    # Change the points immediately after a "transport" sequence to "end".
    df.loc[
        (
            (temp_df_prev[status_col] == "start")
            | (temp_df_prev[status_col] == "transport")
        )
        & ((df[status_col] == "stationary") | (df[status_col] == "pause")),
        status_col,
    ] = "end"

    # Change the points immediately before a "transport" sequence to "start"
    df.loc[
        (temp_df_next[status_col] == "transport")
        & ((df[status_col] == "stationary") | (df[status_col] == "pause")),
        status_col,
    ] = "start"

    df["group"] = (df[status_col] == "start").cumsum().astype("UInt16")
    df.loc[df[status_col] == "stationary", "group"] = pd.NA
    df[id_col] = df.groupby("group")[id_col].transform("first")
    df.drop(columns=["group"], inplace=True)


def adjust_stationary_statutes(df: pd.DataFrame):
    """
    Adjusts the 'trip_status' of 'pause' groups in the DataFrame.

    This function modifies the input DataFrame to change the 'trip_status' of 'pause' groups to 'stationary' under certain conditions.
    If the first or last group is 'pause', it changes the group to 'stationary'.
    It also changes 'pause' groups to 'stationary' if either the previous group or the next group is 'stationary'.

    Args:
        df (pd.DataFrame): The input DataFrame to process. It must contain a 'trip_status' column and a 'group' column.

    Returns:
        None. The function modifies df in-place.
    """
    # Create a new column 'group' that increments by 1 whenever the 'trip_status' changes
    df["group"] = (df["trip_status"] != df["trip_status"].shift()).cumsum()

    # Get the minimum group ID.
    min_id = df["group"].min()

    # Get the maximum group ID.
    max_id = df["group"].max()

    # If the first or last group is 'pause', change the group to 'stationary', so the trip starts and ends with 'stationary'.
    if df["trip_status"].iloc[0] == "pause":
        df.loc[df["group"] == min_id, "trip_status"] = "stationary"

    if df["trip_status"].iloc[-1] == "pause":
        df.loc[df["group"] == max_id, "trip_status"] = "stationary"

    def adjust_group(group, df):
        # Function to apply to each group.
        # If the group is 'pause' and either the previous group or the next group is 'stationary', change the group to 'stationary'.
        if group["trip_status"].iloc[0] == "pause":
            prev_group_status = (
                df.loc[df["group"] == group.name - 1, "trip_status"].values[-1]
                if group.name > min_id
                else None
            )
            next_group_status = (
                df.loc[df["group"] == group.name + 1, "trip_status"].values[0]
                if group.name < max_id
                else None
            )

            if prev_group_status == "stationary" or next_group_status == "stationary":
                group["trip_status"] = "stationary"

        return group

    df = (
        df.groupby("group", as_index=False)
        .apply(lambda x: adjust_group(x, df))
        .reset_index(level=0, drop=True)
    )  # type: ignore

    df.drop("group", axis=1, inplace=True)

    return df


def add_ids(
    df: pd.DataFrame, column: str, target_values: list[str], id_column: str
) -> None:
    """
    Adds a new column to the DataFrame with unique IDs for each group of consecutive rows that match the target values.

    This function modifies the input DataFrame to add a new column with unique IDs. Each group of consecutive rows where the value in the specified column matches one of the target values is given a unique ID. Rows that don't match any of the target values are given an ID of NA.

    Args:
        df (pd.DataFrame): The input DataFrame to process.
        column (str): The name of the column in df to check for target values.
        target_values (list[str]): The values to check for in the specified column.
        id_column (str): The name of the new column to add to df. This column will contain the unique IDs.

    Returns:
        None. The function modifies df in-place.
    """
    # Create a mask that changes value every time one of the target values appears after a different value
    mask = df[column].isin(target_values) & (~df[column].shift().isin(target_values))

    # Use cumsum to generate the ID
    df[id_column] = mask.cumsum().astype("UInt16")

    # Set ID to NA for rows that don't match any of the target values
    df.loc[~df[column].isin(target_values), id_column] = pd.NA


def remove_trips_by_duration(df: pd.DataFrame, min_duration: timedelta) -> None:
    """
    Removes trips from the DataFrame that are shorter than a specified minimum duration.

    Args:
        df (pd.DataFrame): The DataFrame containing the trips.
        min_duration (timedelta): The minimum duration for a trip to be kept in the DataFrame.

    Returns:
        None: The function modifies the DataFrame in-place, and does not return anything.
    """

    trips = df[
        df["trip_id"].notna()
        & df["trip_status"].isin(["start", "transport", "end", "start-end"])
    ].copy()

    # Calculate the duration for each trip.
    trips = trips.groupby(["segment_id", "trip_id"], as_index=False).apply(
        lambda x: x.index.max() - x.index.min()
    )
    trips.rename(columns={None: "duration"}, inplace=True)  # type: ignore

    # Select only the trips that are shorter than the minimum duration.
    removed_trips = trips[trips["duration"] < min_duration][["segment_id", "trip_id"]]

    if not removed_trips.empty:
        # Change rows based on both segment_id and trip_id and set the trip_id and trip_status to NA.
        mask = df.set_index(["segment_id", "trip_id"]).index.isin(
            removed_trips.set_index(["segment_id", "trip_id"]).index
        )
        df.loc[mask, "trip_id"] = pd.NA
        # df.loc[mask, "trip_status"] = (
        #     pd.NA  # HACK: Possibly set this to "stationary" if removed trips should be part of locations, but then need to adjust the stationary_id as well.
        # )
        df.loc[mask, "trip_status"] = "stationary"
        df.loc[mask, "stationary_id"] = df.loc[mask, "stationary_id"].ffill()


def remove_trips_by_length(df: pd.DataFrame, min_length: int | float, crs: str) -> None:
    """
    Removes trips from a DataFrame based on their length.

    Args:
        df (pd.DataFrame): The DataFrame containing the trips.
        min_length (int | float): The minimum length for a trip to be kept in the DataFrame.
        crs (str): The coordinate reference system of the trips.

    Returns:
        None: The function modifies the DataFrame in-place, and does not return anything.
    """
    # Select only the rows that are part of a trip.
    trips = df[
        df["trip_id"].notna()
        & df["trip_status"].isin(["start", "transport", "end", "start-end"])
    ][["segment_id", "trip_id", "latitude", "longitude"]].copy()

    # Calculate the distance traveled for each trip.
    trips = trips.groupby(["segment_id", "trip_id"], as_index=False).apply(
        lambda x: add_distance(x, crs=crs)["distance"].sum()
    )
    trips.rename(columns={None: "length"}, inplace=True)  # type: ignore

    # Select only the trips that are shorter than the minimum length.
    removed_trips = trips[trips["length"] < min_length][["segment_id", "trip_id"]]

    if not removed_trips.empty:
        # Change rows based on both segment_id and trip_id and set the trip_id and trip_status to NA.
        mask = df.set_index(["segment_id", "trip_id"]).index.isin(
            removed_trips.set_index(["segment_id", "trip_id"]).index
        )
        df.loc[mask, "trip_id"] = pd.NA
        # df.loc[mask, "trip_status"] = (
        #     pd.NA  # HACK: Possibly set this to "stationary" if removed trips should be part of locations, but then need to adjust the stationary_id as well.
        # )
        df.loc[mask, "trip_status"] = "stationary"
        df.loc[mask, "stationary_id"] = df.loc[mask, "stationary_id"].ffill()


def _change_indoor_trip_to_stationary(df: pd.DataFrame, limit: float) -> str | None:
    environment = df["environment"].value_counts()
    dominant_environment = environment.idxmax()

    if len(environment) >= 2 and dominant_environment == "indoor" and limit:
        total_values = environment.sum()
        dominant_values = environment[dominant_environment]

        if (dominant_values / total_values * 100) <= limit:
            return None

    return dominant_environment  # type: ignore


def remove_indoor_trips(df: pd.DataFrame, indoor_limit: float):
    # Select only the rows that are part of a trip.
    trips = df[
        df["trip_id"].notna()
        & df["trip_status"].isin(["start", "transport", "end", "start-end"])
    ].copy()

    trips = trips.groupby(["segment_id", "trip_id"], as_index=False).apply(
        lambda x: _change_indoor_trip_to_stationary(x, indoor_limit)  # type: ignore
    )

    if not trips.empty:
        trips.rename(columns={None: "environment"}, inplace=True)  # type: ignore
        trips = trips.astype({"environment": "category"})

        removed_trips = trips[trips["environment"] == "indoor"][
            ["segment_id", "trip_id"]
        ]

        # Change rows based on both segment_id and trip_id and set the trip_id and trip_status to NA.
        mask = df.set_index(["segment_id", "trip_id"]).index.isin(
            removed_trips.set_index(["segment_id", "trip_id"]).index
        )
        df.loc[mask, "trip_id"] = pd.NA
        # df.loc[mask, "trip_status"] = (
        #     pd.NA  # HACK: Possibly set this to "stationary" if removed trips should be part of locations, but then need to adjust the stationary_id as well.
        # )
        df.loc[mask, "trip_status"] = "stationary"
        df.loc[mask, "stationary_id"] = df.loc[mask, "stationary_id"].bfill()


def get_segment_trips(
    df: pd.DataFrame,
    crs: str,
    sampling_frequency: float,
    stop_radius: int | float,
    stop_duration: timedelta,
    pause_radius: int | float | None = None,
    pause_duration: timedelta | None = None,
    min_distance: int | float | None = None,
    max_speed: int | float | None = None,
):
    """
    Processes the given DataFrame to identify and label trips based on various parameters.

    This function applies several filters to the DataFrame, including a minimum distance filter and a maximum speed filter.
    It then identifies and labels trips based on the given maximum radius, stop duration, and pause duration.

    Args:
        df (pd.DataFrame): The input DataFrame to process.
        crs (str): The coordinate reference system to use when processing the DataFrame. The latitude and longitude columns must be in this CRS, otherwise the results will be incorrect.
        sampling_frequency (float): The sampling frequency of the data in seconds. This is used to convert the minimum distance to the correct units.
        max_radius (int | float): The maximum radius to use when splitting stops.
        stop_duration (timedelta): The minimum duration to consider a stop.
        pause_duration (timedelta): The minimum duration to consider a pause.
        min_distance (int | float | None, optional): The minimum distance between points. Points that are closer than this distance are filtered out. If None, no minimum distance filter is applied.
        max_speed (int | float | None, optional): The maximum speed. Points that are faster than this speed are filtered out. If None, no maximum speed filter is applied.

    Returns:
        pd.DataFrame: The processed DataFrame with added 'trip_id', 'trip_status' columns.
    """
    origin = df

    # Filter out points that are too close to each other.
    if min_distance is not None:
        min_distance = convert_distance_parameter(min_distance, sampling_frequency)
        df = min_distance_filter(df, min_distance=min_distance, crs=crs)
        df = df[df["min_distance"]]  # type: ignore

    # Filter out points that are too fast.
    if max_speed is not None:
        df = max_speed_filter(df, max_speed=max_speed, crs=crs)
        df = df[df["max_speed"]]  # type: ignore

    # Get the trips from the DataFrame.
    df = get_trips(df, crs=crs, stop_radius=stop_radius, stop_duration=stop_duration)

    # Get the pauses from the DataFrame.
    if not pause_radius and not pause_duration:
        pauses = pd.Series(name="partial_status")
    else:
        if not pause_radius:
            pause_radius = stop_radius

        if not pause_duration:
            pause_duration = stop_duration

        pauses = get_pauses(
            df, crs=crs, pause_radius=pause_radius, pause_duration=pause_duration
        )

    # Merge the pauses with the trips if there are any.
    if not pauses.empty:
        df = df.join(
            pauses,
            how="left",
        )
        df["trip_status"] = df["partial_status"].combine_first(df["trip_status"])
        df.drop(columns=["partial_status"], inplace=True)

        # Change the pause status to 'stationary' if necessary, so if pause follows a stationary point, it is also stationary.
        df = adjust_stationary_statutes(df)

    # Fix the start and end of trips and locations.
    add_ids(df, "trip_status", ["pause", "transport"], "trip_id")
    add_ids(
        df,
        "trip_status",
        ["pause", "stationary"],
        "stationary_id",
    )

    # Add start and end boundaries to trips.
    add_boundaries(df, id_col="trip_id", status_col="trip_status", extremities=True)

    # Merge the processed DataFrame with the original DataFrame.
    origin = origin.join(
        df[["trip_status", "trip_id", "stationary_id"]],
        how="left",
    )

    return origin


# TODO: Fix docstring.
def detect_trips(
    df: pd.DataFrame,
    *,
    crs: str,
    sampling_frequency: float,
    gap_duration: timedelta,
    stop_radius: int | float,
    stop_duration: timedelta,
    pause_radius: int | float | None = None,
    pause_duration: timedelta | None = None,
    min_duration: timedelta | None = None,
    min_length: int | float | None = None,
    min_distance: int | float | None = None,
    max_speed: int | float | None = None,
    indoor_limit: float | None = None,
    overwrite: bool = False,
) -> pd.DataFrame:
    """
    Detects trips in the given DataFrame based on various parameters.

    This function applies several filters to the DataFrame, including a minimum length filter, a minimum distance filter, and a maximum speed filter.
    It then identifies and labels trips based on the given maximum radius, stop duration, and pause duration.
    It also splits the DataFrame into segments based on the given gap duration.

    Args:
        df (pd.DataFrame): The input DataFrame to process. It must not contain 'segment_id', 'trip_id', and 'trip_status' columns.
        crs (str): The coordinate reference system to use when processing the DataFrame. The latitude and longitude columns must be in this CRS, otherwise the results will be incorrect.
        sampling_frequency (float): The sampling frequency of the data in seconds.
        gap_duration (timedelta): The minimum duration to consider a gap, i.e. if there is missing data for longer than this duration, the data is split into a new segment.
        max_radius (int | float): The maximum radius that subject needs to stay in to be considered a stop or pause.
        stop_duration (timedelta): The minimum duration to subject need to stay in specified radius to be considered a stop.
        pause_duration (timedelta): The minimum duration to subject need to stay in specified radius to be considered a pause.
        min_duration (int | float | None, optional): The minimum duration of a trip. Trips that are shorter than this duration are filtered out. If None, filter is not applied.
        min_length (int | float | None, optional): The minimum length of a trip. Trips that are shorter than this length are filtered out. If None, filter is not applied.
        min_distance (int | float | None, optional): The minimum distance between points. Points that are closer than this distance are filtered out. If None, filter is not applied.
        max_speed (int | float | None, optional): The maximum speed. Speed between points that are faster than this speed are filtered out. If None, filter is not applied.

    Returns:
        pd.DataFrame: The processed DataFrame with updated 'trip_id' and 'trip_status' columns.
    """

    # TODO: Check sampling frequency against some parameters, e.g. if sampling frequency is 2 minute, we can't have a gap_duration of 1 minute etc. Check what happens if some parameters are the same as sampling frequency.
    if (not min_duration or min_duration == 0) and (not min_length or min_length == 0):
        raise ValueError("Both 'min_duration' and 'min_length' cannot be None or zero.")

    if df.empty:
        raise ValueError("The input DataFrame is empty.")

    columns_not_exists(
        df,
        ["segment_id", "trip_id", "trip_status", "stationary_id"],
        overwrite=overwrite,
    )

    working_cols = ["latitude", "longitude"]

    # Get the segments from the DataFrame.
    segments = gap_splitter(
        df[working_cols],
        name="segment_id",
        min_duration=gap_duration,
        overwrite=overwrite,
    )
    df = df.join(
        segments[["segment_id"]],
        how="left",
    )

    working_cols.append("segment_id")
    if "environment" in df.columns:
        working_cols.append("environment")

    temp_df = (
        df[working_cols]
        .groupby("segment_id")
        .apply(
            lambda x: get_segment_trips(
                x,
                crs=crs,
                sampling_frequency=sampling_frequency,
                stop_radius=stop_radius,
                stop_duration=stop_duration,
                pause_radius=pause_radius,
                pause_duration=pause_duration,
                min_distance=min_distance,
                max_speed=max_speed,
            )
        )
        .reset_index(level=0, drop=True)
    )  # type: ignore

    # Remove trips that are too short (duration).
    if min_duration:
        remove_trips_by_duration(temp_df, min_duration=min_duration)

    # Remove trips that are too short (length).
    if min_length:
        remove_trips_by_length(temp_df, min_length=min_length, crs=crs)

    if "environment" in temp_df.columns and indoor_limit:
        # TODO: Should be this set outside of the function? And maybe just annotated if the trip is indoor or not, so researchers can exclude indoor trips and say that they are stationary.
        remove_indoor_trips(temp_df, indoor_limit)

    temp_df = temp_df[temp_df["trip_status"].notna()]
    trip_mask = temp_df["trip_id"].notna()
    stationary_mask = temp_df["stationary_id"].notna()

    # Renumbers the trip IDs to be unique across all segments.
    temp_df.loc[trip_mask, "trip_id"] = (
        pd.factorize(
            temp_df.loc[trip_mask, "segment_id"].astype(str)
            + temp_df.loc[trip_mask, "trip_id"].astype(str)
        )[0]
        + 1
    )

    # Renumbers the stationary IDs to be unique across all segments.
    temp_df["stationary_id"] = (
        temp_df["stationary_id"].isna().astype(int).diff().ne(0).cumsum()
    ).where(stationary_mask)

    temp_df.loc[stationary_mask, "stationary_id"] = (
        pd.factorize(
            temp_df.loc[stationary_mask, "segment_id"].astype(str)
            + temp_df.loc[stationary_mask, "stationary_id"].astype(str)
        )[0]
        + 1
    )

    # Merge the processed DataFrame with the original DataFrame.
    df = df.join(
        temp_df[["trip_status", "trip_id", "stationary_id"]],
        how="left",
    )

    # Validate the output DataFrame.
    df = SCHEMA.validate(df)

    return df
