from pathlib import Path

import pandas as pd

from .validation.linkage import SCHEMA


def from_csv(path: str | Path) -> pd.DataFrame:
    if isinstance(path, str):
        path = Path(path)

    df = pd.read_csv(
        path,
        dtype={
            "subject_id": "string",
            "sensor_id": "string",
        },
        delimiter=";",
    )

    if "start" in df.columns:
        df["start"] = pd.to_datetime(df["start"], format="%Y-%m-%d %H:%M:%S")

    if "end" in df.columns:
        df["end"] = pd.to_datetime(df["end"], format="%Y-%m-%d %H:%M:%S")

    return SCHEMA.validate(df)
