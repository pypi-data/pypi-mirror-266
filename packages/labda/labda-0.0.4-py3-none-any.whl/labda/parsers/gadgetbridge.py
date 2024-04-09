from datetime import datetime
from pathlib import Path

import pandas as pd
import pytz
from sqlalchemy import Engine, MetaData, Table, create_engine, select

from ..structure.subject import Metadata, Sensor, Subject, Vendor
from ..structure.validation.subject import SCHEMA, Column
from ..utils import get_sampling_frequency

# TODO: This should be refactored, so it gets subject one by one from database based on datetime range.
# TODO: Add docstrings


def _get_xiaomi_records(
    engine: Engine,
    *,
    start: datetime | None = None,
    end: datetime | None = None,
    ids: list[str] | None = None,
) -> pd.DataFrame:
    metadata = MetaData()
    band_activity = Table("MI_BAND_ACTIVITY_SAMPLE", metadata, autoload_with=engine)  # type: ignore

    # RAW_KIND explained: https://codeberg.org/Freeyourgadget/Gadgetbridge/issues/686
    query = select(
        band_activity.c.TIMESTAMP,
        band_activity.c.DEVICE_ID,
        band_activity.c.STEPS,
        band_activity.c.HEART_RATE,
    )

    if ids:
        query = query.where(band_activity.c.DEVICE_ID.in_(ids))

    if start:
        query = query.where(band_activity.c.TIMESTAMP >= start.timestamp())

    if end:
        query = query.where(band_activity.c.TIMESTAMP <= end.timestamp())

    if start and end:
        if end < start:
            raise ValueError("The end time must be after the start time.")

    records = pd.read_sql_query(
        query,
        engine,
        parse_dates=["TIMESTAMP"],
        dtype={"DEVICE_ID": "UInt16", "STEPS": "UInt8", "HEART_RATE": "UInt8"},
    )
    records.rename(
        columns={
            "TIMESTAMP": Column.DATETIME,
            "DEVICE_ID": "device_id",
            "STEPS": Column.STEPS,
            "HEART_RATE": Column.HEART_RATE,
        },
        inplace=True,
    )

    records.loc[records[Column.HEART_RATE] == 255, Column.HEART_RATE] = None

    return records


def _get_xiaomi_devices(
    engine: Engine, *, linkage: pd.DataFrame | None = None
) -> pd.DataFrame:
    metadata = MetaData()
    device = Table("DEVICE", metadata, autoload_with=engine)  # type: ignore
    query = select(
        device.c._id, device.c.NAME, device.c.IDENTIFIER, device.c.ALIAS, device.c.MODEL
    )

    if isinstance(linkage, pd.DataFrame) and not linkage.empty:
        mac = linkage["sensor_id"].to_list()  # type: ignore
        query = query.where(device.c.IDENTIFIER.in_(mac))

    devices = pd.read_sql_query(
        query,
        engine,
        dtype={
            "_id": "UInt16",
            "NAME": "string",
            "IDENTIFIER": "string",
            "ALIAS": "string",
            "IDENTIFIER": "string",
        },
    )
    devices.rename(
        columns={
            "_id": "device_id",
            "NAME": "model",
            "IDENTIFIER": "serial_number",
            "MODEL": "firmware_version",
            "ALIAS": "alias",
        },
        inplace=True,
    )

    if isinstance(linkage, pd.DataFrame) and not linkage.empty:
        devices = devices.merge(
            linkage, left_on="serial_number", right_on="sensor_id", how="left"
        )
        devices.drop(columns=["sensor_id"], inplace=True)
    else:
        devices[Column.SUBJECT_ID] = devices["serial_number"]

    return devices


def _get_wear_by_hr(df: pd.DataFrame, limit: int | None = None) -> pd.DataFrame:
    df = df.copy()
    df[Column.WEAR] = pd.NA
    df.loc[df[Column.HEART_RATE].notna(), Column.WEAR] = True

    if limit:
        df[Column.WEAR] = df[Column.WEAR].bfill(limit=limit)

    df.loc[df[Column.WEAR].isna(), Column.WEAR] = False

    return df


def _get_xiaomi(
    engine: Engine,
    *,
    start: datetime | None,
    end: datetime | None,
    linkage: pd.DataFrame | None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    devices = _get_xiaomi_devices(engine, linkage=linkage)

    ids = devices["device_id"].to_list() if not devices.empty else None
    records = _get_xiaomi_records(engine, start=start, end=end, ids=ids)
    records = records.merge(
        devices[[Column.SUBJECT_ID, "device_id"]], on="device_id", how="left"
    )
    return (
        records[
            [
                Column.DATETIME,
                Column.SUBJECT_ID,
                Column.STEPS,
                Column.HEART_RATE,
            ]
        ],
        devices,
    )


def _generate_records(
    records: pd.DataFrame,
    devices: pd.DataFrame,
) -> list[Subject]:
    # TODO: Add docstring.
    # TODO: Maybe force resampling for making sure that all records have the same frequency.
    records = records.groupby(Column.SUBJECT_ID, as_index=False)  # type: ignore
    objs = []
    for record in records:
        id = record[0]  # type: ignore
        df = record[1]  # type: ignore
        df.set_index(Column.DATETIME, inplace=True)
        df = _get_wear_by_hr(df, 4)
        df = SCHEMA.validate(df)

        sampling_frequency = get_sampling_frequency(df)

        device = devices.loc[devices[Column.SUBJECT_ID] == id].iloc[0].to_dict()
        sensor = Sensor(id=device["serial_number"], **device, vendor=Vendor.XIAOMI)
        metadata = Metadata(
            id=id,  # type: ignore
            sensor=[sensor],
            sampling_frequency=sampling_frequency,
        )

        objs.append(Subject(metadata=metadata, df=df))

    return objs


def from_xiaomi(
    path: str | Path,
    *,
    start: datetime | None = None,
    end: datetime | None = None,
    linkage: pd.DataFrame | None = None,
    timezone: str = "UTC",
) -> list[Subject]:
    # TODO: Rewrite docstring, different return type.
    # TODO: Something to check timezone - if start-end is TZ aware, then no need to guess timezone, if not - guess it.
    if isinstance(path, str):
        path = Path(path)

    if not path.is_file():
        raise ValueError(f"Invalid file path: {path}")

    engine = create_engine(f"sqlite:///{path.as_posix()}")

    utc = pytz.timezone("UTC")
    timezone = pytz.timezone(timezone)  # type: ignore

    if start:
        start = timezone.localize(start).astimezone(utc)  # type: ignore

    if end:
        end = timezone.localize(end).astimezone(utc)  # type: ignore

    records, devices = _get_xiaomi(
        engine,
        start=start,
        end=end,
        linkage=linkage,
    )

    records[Column.DATETIME] = (
        records[Column.DATETIME]
        .dt.tz_localize(pytz.timezone("UTC"))
        .dt.tz_convert(timezone)
    ).dt.tz_localize(None)

    subjects = _generate_records(records, devices)

    return subjects
