from datetime import datetime
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd

from ..logging import success_parsing_log
from ..structure.subject import Metadata, Sensor, Subject, Vendor
from ..structure.validation.subject import SCHEMA, Column
from ..utils import (
    align_datetimes,
    columns_exists,
    filter_datetime,
    get_sampling_frequency,
)
from .utils import set_crs, set_timezone

# TODO: Can be refactored.,


def detect_environment_from_gps_signal(
    df: pd.DataFrame,
    method: str,
    limit: int | float,
) -> pd.DataFrame:
    df = df.copy()

    methods = [
        Column.SNR_USED,  # 225 (F1: 46,80)
        Column.SNR_VIEWED,  # 260 (F1: 71,18)
        Column.NSAT_USED,  # 7 (F1: 48,86)
        Column.NSAT_VIEWED,  # 9 (F1: 42,93)
        Column.NSAT_RATIO,  # 70 (F1: 46,40)
    ]
    if method not in methods:
        raise ValueError(f"Method muset be one of {methods}")

    if method not in df.columns:
        raise ValueError(f"Column '{method}' does not exist in dataframe")

    mask = df[method].notna()
    df.loc[mask, Column.ENVIRONMENT] = "outdoor"
    df.loc[mask & (df[method] <= limit), Column.ENVIRONMENT] = "indoor"

    return df


def parse_snr(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    sat_info_4 = "SAT INFO (SID-ELE-AZI-SNR)"
    sat_info_2 = "SAT INFO (SID-SNR)"
    snr = "SNR"

    column = None

    if sat_info_2 in df.columns:
        column = sat_info_2
    elif sat_info_4 in df.columns:
        column = sat_info_4
    elif snr in df.columns:
        column = snr

    if column:
        df.loc[df[column].str.contains("/"), column] = pd.NA
        temp_df = df[df[column].notna()].copy()
        temp_df[column] = temp_df[column].str.split(";")
        temp_df[column] = temp_df[column].apply(
            lambda row: [int(signal.split("-")[-1]) for signal in row]
        )
        temp_df[Column.SNR_VIEWED] = temp_df[column].apply(lambda row: sum(row))
        columns = [Column.SNR_VIEWED]

        if Column.NSAT_USED in temp_df.columns:
            temp_df[Column.SNR_USED] = temp_df.apply(
                lambda row: sum(row[column][: row[Column.NSAT_USED]]), axis=1
            )
            columns.append(Column.SNR_USED)

        if Column.NSAT_VIEWED not in temp_df.columns:
            temp_df[Column.NSAT_VIEWED] = temp_df[column].apply(lambda row: len(row))
            columns.append(Column.NSAT_VIEWED)

        df = df.join(temp_df[columns])

    return df


def parse_nsat(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    possible_columns = ["NSAT (USED/VIEW)", "NSAT(USED/VIEW)", "NSAT(USED/VIEWED)"]

    for column in possible_columns:
        if column in df.columns:
            nsat_uv = "NSAT (USED/VIEW)"
            df.rename(columns={column: nsat_uv}, inplace=True)
            break

    nsat = "NSAT"

    if nsat_uv in df.columns:
        if df[nsat_uv].str.contains("/").any():
            df[nsat_uv] = df[nsat_uv].str.split("/")
        elif df[nsat_uv].str.contains("\(").any():
            df[nsat_uv] = df[nsat_uv].str.replace(")", "").str.split("(")
        df[Column.NSAT_USED] = pd.to_numeric(df[nsat_uv].str[0])
        df[Column.NSAT_VIEWED] = pd.to_numeric(df[nsat_uv].str[1])
    elif nsat in df.columns:
        df.rename(columns={nsat: Column.NSAT_USED}, inplace=True)
        df[Column.NSAT_USED] = pd.to_numeric(df[Column.NSAT_USED])

    return df


def parse_dop(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    column_mapping = {
        "HDOP": Column.HDOP,
        "VDOP": Column.VDOP,
        "PDOP": Column.PDOP,
    }

    for old_column, new_column in column_mapping.items():
        if old_column in df.columns:
            df.rename(columns={old_column: new_column}, inplace=True)

    return df


def parse_speed(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    column = None
    speed_kmh = "SPEED(km/h)"
    speed = "SPEED"

    if speed in df.columns:
        column = speed
    elif speed_kmh in df.columns:
        column = speed_kmh

    if column:
        if df[column].dtype == "object":
            df[column] = df[column].str.strip("km/h")
        df[column] = pd.to_numeric(df[column])
        df[column] = (df[column] / 3.6).round(2)
        df.rename(columns={column: Column.SPEED}, inplace=True)

    return df


def parse_distance(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    column = None
    distance_km = "DISTANCE(m)"

    if distance_km in df.columns:
        column = distance_km

    if column:
        df[column] = pd.to_numeric(df[column])
        df[column] = df[column].round(2)
        df.rename(columns={column: Column.DISTANCE}, inplace=True)

    return df


def parse_elevation(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    column = None
    height_m = "HEIGHT(m)"
    height = "HEIGHT"

    if height_m in df.columns:
        column = height_m
    elif height in df.columns:
        column = height

    if df[column].dtype == "object":
        df[column] = df[column].str.strip("M")
    df[column] = pd.to_numeric(df[column])
    df[column] = df[column].round(2)
    df.rename(columns={column: Column.ELEVATION}, inplace=True)
    return df


def parse_datetime(df: pd.DataFrame, dt_format: str | None = None) -> pd.DataFrame:
    df = df.copy()
    column = None

    if "DATE" in df.columns and "TIME" in df.columns:
        date = "DATE"
        time = "TIME"
    elif "LOCAL DATE" in df.columns and "LOCAL TIME" in df.columns:
        date = "LOCAL DATE"
        time = "LOCAL TIME"
    elif "LOCAL TIME" in df.columns:
        column = "LOCAL TIME"

    else:
        raise ValueError("The date and time columns are missing.")

    if column:
        df.rename(columns={column: Column.DATETIME}, inplace=True)
    else:
        df = df.astype({date: "string", time: "string"})
        df[Column.DATETIME] = df[date] + " " + df[time]
        df.drop(columns=[date, time], inplace=True)

    df[Column.DATETIME] = pd.to_datetime(df[Column.DATETIME], format=dt_format)

    return df


def parse_coordinates(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    columns_exists(df, ["LATITUDE", "LONGITUDE", "N/S", "E/W"])
    df.rename(
        columns={"LATITUDE": Column.LATITUDE, "LONGITUDE": Column.LONGITUDE},
        inplace=True,
    )
    df[[Column.LATITUDE, Column.LONGITUDE]] = df[
        [Column.LATITUDE, Column.LONGITUDE]
    ].apply(pd.to_numeric)

    df["N/S"] = df["N/S"].str.strip()
    df[Column.LATITUDE] = np.where(
        df["N/S"] == "S", -df[Column.LATITUDE], df[Column.LATITUDE]
    )

    df["E/W"] = df["E/W"].str.strip()
    df[Column.LONGITUDE] = np.where(
        df["E/W"] == "W", -df[Column.LONGITUDE], df[Column.LONGITUDE]
    )

    return df


def drop_empty_columns(df: pd.DataFrame) -> None:
    """
    Drops the columns with empty names from the DataFrame.

    This function identifies the columns with empty names in the DataFrame and drops them in-place.

    Args:
        df (pd.DataFrame): The DataFrame from which to drop the columns with empty names.

    Returns:
        None
    """
    columns_to_drop = df.columns[(df.columns == "")]
    df.drop(columns=columns_to_drop, inplace=True)


def remove_repeated_headers(df: pd.DataFrame) -> None:
    """
    Removes the rows from the DataFrame that are identical to the header.

    This function identifies the rows that are identical to the header in the DataFrame and removes them in-place.

    Args:
        df (pd.DataFrame): The DataFrame from which to remove the rows identical to the header.

    Returns:
        None
    """
    header = pd.Series(df.columns, df.columns)
    same_as_header = df[df.eq(header).all(axis=1)].index
    df.drop(same_as_header, inplace=True)


def from_csv(
    path: str | Path,
    *,
    subject_id: str | None = None,
    sensor_id: str | None = None,
    serial_number: str | None = None,
    model: str | None = None,
    vendor: Vendor = Vendor.QSTARZ,
    firmware_version: str | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    sampling_frequency: float | None = None,
    crs: str | None | Tuple[str, str] = None,
    timezone: str | None | Tuple[str, str] = None,
    datetime_format: str | None = None,
    nsat_ratio: float = 70,
    snr_viewed: int = 260,
) -> Subject:
    if isinstance(path, str):
        path = Path(path)

    if not path.is_file():
        raise ValueError(f"Invalid file path: {path}")

    if path.suffix != ".csv":
        raise ValueError(f"Invalid file extension: {path.suffix}")

    df = pd.read_csv(path, engine="pyarrow")
    drop_empty_columns(df)
    df.columns = df.columns.str.strip()

    remove_repeated_headers(df)

    df = parse_coordinates(df)
    df = parse_datetime(df, datetime_format)

    df.drop_duplicates(
        subset=[Column.DATETIME], inplace=True
    )  # If there are duplicates, keep only the first one - because later with resample, datetime needs to be unique.

    # Remove rows with "Estimated (dead reckoning)" in the "VALID" column.
    if "VALID" in df.columns:
        df = df[~(df["VALID"] == "Estimated (dead reckoning)")]

    df = parse_distance(df)
    df = parse_speed(df)
    df = parse_elevation(df)
    df = parse_dop(df)
    df = parse_nsat(df)
    df = parse_snr(df)

    if Column.NSAT_USED in df.columns and Column.NSAT_VIEWED in df.columns:
        df[Column.NSAT_RATIO] = (
            (df[Column.NSAT_USED] * 100) / df[Column.NSAT_VIEWED]
        ).round(2)

    if Column.SNR_VIEWED in df.columns and snr_viewed:
        df = detect_environment_from_gps_signal(df, Column.SNR_VIEWED, snr_viewed)
    elif Column.NSAT_RATIO in df.columns and nsat_ratio:
        df = detect_environment_from_gps_signal(df, Column.NSAT_RATIO, nsat_ratio)

    df.set_index(Column.DATETIME, inplace=True)
    df, timezone = set_timezone(df, timezone)
    df, crs = set_crs(df, crs)

    df = filter_datetime(df, start, end)

    if not sampling_frequency:
        sampling_frequency = get_sampling_frequency(df)

    df = align_datetimes(df, sampling_frequency)

    # Order columns as defined in Column, remove extra columns
    records_columns = [col.value for col in Column]
    ordered_columns = [col for col in records_columns if col in df.columns]
    df = df[ordered_columns]

    df = SCHEMA.validate(df)

    subject_id = subject_id or path.stem
    sensor_id = sensor_id or path.stem

    sensor = Sensor(
        id=sensor_id,
        serial_number=serial_number,
        model=model,
        vendor=vendor,
        firmware_version=firmware_version,
    )

    metadata = Metadata(
        id=subject_id,
        sensor=[sensor],
        sampling_frequency=sampling_frequency,
        crs=crs,
        timezone=timezone,
    )

    subject = Subject(metadata=metadata, df=df)

    func = f"{__name__}:from_csv"
    success_parsing_log(subject, path, func)

    return subject
