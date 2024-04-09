from datetime import timedelta

import pandas as pd

from ...expanders.accelerometer import add_counts_vector_magnitude
from ...processing.bouts import get_bouts
from ...structure.validation.subject import Column
from ...utils import columns_not_exists


def detect_wear(
    df: pd.DataFrame,
    sampling_frequency: float,
    min_duration: timedelta,
    *,
    interruption_duration: timedelta | None = None,
    name: str = Column.WEAR,
    overwrite: bool = False,
) -> pd.DataFrame:
    columns_not_exists(df, [name], overwrite=overwrite)

    if Column.VM_COUNTS not in df.columns:
        df = add_counts_vector_magnitude(df)

    df = get_bouts(
        df,
        Column.VM_COUNTS,
        sampling_frequency,
        min_duration,
        0,
        0,
        interruption_duration=interruption_duration,
        name=name,
        overwrite=overwrite,
    )
    df[name] = ~df[name]

    return df
