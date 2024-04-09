from datetime import datetime
from pathlib import Path
from typing import Any, Tuple

import pandas as pd
from dateutil.parser import parse as parse_dt

from ..logging import success_parsing_log
from ..structure.subject import Metadata, Sensor, Subject, Vendor
from ..structure.validation.subject import SCHEMA, Column
from ..utils import (
    align_datetimes,
    filter_datetime,
    get_sampling_frequency,
)
from .utils import set_timezone

# TODO: Add param for column mapping if there is no header.
# TODO: It is not perfect, but it is a start and it should be able to parse automatically almost all ActiGraph files from SDU.


def get_metadata(metadata: list[str]) -> dict[str, Any]:
    model = metadata[0].split("ActiGraph")[-1].split()[0].strip()
    firmware = metadata[0].split("Firmware")[-1].split()[0].strip()
    serial_number = metadata[1].split()[-1].strip()
    start_time = metadata[2].split()[-1].strip()
    start_date = metadata[3].split()[-1].strip()
    start_datetime = parse_dt(start_date + " " + start_time)
    sampling_frequency = pd.to_timedelta(
        metadata[4].split()[-1].strip()
    ).total_seconds()

    return {
        "model": model,
        "firmware": firmware,
        "serial_number": serial_number,
        "start_datetime": start_datetime,
        "sampling_frequency": sampling_frequency,
    }


def handle_dataframe_header(data: list[str]) -> pd.DataFrame:
    data_header = data[0].split(",")
    data = data[1:]
    df = pd.DataFrame(data)
    df = df[0].str.split(",", expand=True)
    df.columns = data_header
    df.columns = df.columns.str.strip().str.lower()

    column_mapping = {
        "epoch": "time",
        "axis1": Column.VERTICAL_COUNTS,
        "axis2": Column.HORIZONTAL_COUNTS,
        "axis3": Column.PERPENDICULAR_COUNTS,
        "activity": Column.VERTICAL_COUNTS,
        "activity (horizontal)": Column.HORIZONTAL_COUNTS,
        "3rd axis": Column.PERPENDICULAR_COUNTS,
        "vector magnitude": Column.VM_COUNTS,
        "vm": Column.VM_COUNTS,
        "steps": Column.STEPS,
        "lux": Column.LUX,
        "inclinometer off": "non-wear",
        "inclinometer standing": "standing",
        "inclinometer sitting": "sitting",
        "inclinometer lying": "lying",
    }

    for old_column, new_column in column_mapping.items():
        if old_column in df.columns:
            df.rename(columns={old_column: new_column}, inplace=True)

    if Column.VM_COUNTS in df.columns and df[Column.VM_COUNTS].dtype == object:
        df[Column.VM_COUNTS] = df[Column.VM_COUNTS].str.replace('"', "")

    return df


def handle_inclinometer(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    columns = ["non-wear", "standing", "sitting", "lying"]
    exists_columns = []

    for column in columns:
        if column in df.columns:
            exists_columns.append(column)

    if exists_columns:
        df[Column.POSITION] = df[exists_columns].idxmax(axis=1)

    if "non-wear" in exists_columns:
        df[Column.WEAR] = True
        df.loc[df[Column.POSITION] == "non-wear", Column.WEAR] = False
        df.loc[df[Column.WEAR] == False, Column.POSITION] = pd.NA

    df.drop(columns=exists_columns, inplace=True)

    return df


def handle_datetime(
    df: pd.DataFrame,
    metadata: dict[str, Any],
    dt_format: str | None = None,
) -> pd.DataFrame:
    df = df.copy()

    if "date" in df.columns and "time" in df.columns:
        df[Column.DATETIME] = pd.to_datetime(
            df["date"] + " " + df["time"], format=dt_format
        )
        df.drop(columns=["date", "time"], inplace=True)
    elif metadata.get("start_datetime") and metadata.get("sampling_frequency"):
        start_datetime = metadata["start_datetime"]
        sampling_frequency = metadata["sampling_frequency"]
        df[Column.DATETIME] = start_datetime + pd.to_timedelta(
            df.index * sampling_frequency, unit="s"
        )

    return df


def from_csv(
    path: str | Path,
    line: int = 10,
    metadata: bool = True,
    *,
    subject_id: str | None = None,
    sensor_id: str | None = None,  # type: ignore
    serial_number: str | None = None,
    model: str | None = None,
    vendor: Vendor = Vendor.ACTIGRAPH,
    firmware_version: str | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    timezone: str | None | Tuple[str, str] = None,
    datetime_format: str | None = None,
) -> Subject:
    if isinstance(path, str):
        path = Path(path)

    if not path.is_file():
        raise ValueError(f"Invalid file path: {path}")

    if path.suffix != ".csv":
        raise ValueError(f"Invalid file extension: {path.suffix}")

    with path.open("r") as f:
        file = f.read()

    lines = file.splitlines()

    if metadata:
        parsed_metadata = get_metadata(lines[0:line])
    else:
        parsed_metadata = {}

    data = lines[line:]

    if any(char.isalpha() for char in data[0]):
        df = handle_dataframe_header(data)
        df = handle_inclinometer(df)
    else:
        df = pd.DataFrame(
            data,
        )
        df = df[0].str.split(",", expand=True)
        df = df.iloc[:, :3]
        df.columns = [
            Column.VERTICAL_COUNTS,
            Column.HORIZONTAL_COUNTS,
            Column.PERPENDICULAR_COUNTS,
        ]

    df = handle_datetime(df, parsed_metadata, datetime_format)

    df.set_index(Column.DATETIME, inplace=True)
    df, timezone = set_timezone(df, timezone)

    df = filter_datetime(df, start, end)

    sampling_frequency = parsed_metadata.get("sampling_frequency")
    if not sampling_frequency:
        sampling_frequency = get_sampling_frequency(df)

    df = align_datetimes(df, sampling_frequency)

    columns = [col.value for col in Column]
    ordered_columns = [col for col in columns if col in df.columns]
    df = df[ordered_columns]

    df = SCHEMA.validate(df)

    sensor_id = (
        sensor_id if sensor_id else parsed_metadata.get("serial_number") or path.stem
    )  # type: str
    serial_number = (
        serial_number if serial_number else parsed_metadata.get("serial_number")
    )
    model = model if model else parsed_metadata.get("model")
    firmware_version = (
        firmware_version if firmware_version else parsed_metadata.get("firmware")
    )

    subject_id = subject_id or path.stem

    sensor = Sensor(
        id=sensor_id,
        serial_number=serial_number,
        model=model,
        vendor=vendor,
        firmware_version=firmware_version,
    )  # type: ignore

    metadata = Metadata(
        id=subject_id,
        sensor=[sensor],
        sampling_frequency=sampling_frequency,
        timezone=timezone,
    )  # type: ignore

    subject = Subject(metadata=metadata, df=df)  # type: ignore

    func = f"{__name__}:from_csv"
    success_parsing_log(subject, path, func)

    return subject
