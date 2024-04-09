from pathlib import Path

import pandas as pd
from shapely import wkt

from .validation.domains import SCHEMA


def from_csv(path: str | Path) -> pd.DataFrame:
    # TODO: Check datetime overlap.
    # TODO: Add column for "importance" in case of overlapping domains.
    if isinstance(path, str):
        path = Path(path)

    domains = pd.read_csv(
        path,
        dtype={
            "subject_id": "string",
            "domain": "string",
            "geometry": "string",
        },
        delimiter=";",
        parse_dates=["start", "end"],
        date_format="%Y-%m-%d %H:%M:%S",
    )

    domains["geometry"] = domains["geometry"].apply(wkt.loads)

    return SCHEMA.validate(domains)
