import pandas as pd

from ...structure.validation.subject import Column
from ...utils import columns_exists, columns_not_exists

# TODO: Refactor...


def detect_mvpa_from_steps(
    df: pd.DataFrame,
    sampling_frequency: float,
    name: str = Column.ACTIVITY_INTENSITY,
    overwrite: bool = False,
) -> pd.DataFrame:
    columns_exists(df, [Column.STEPS])
    columns_not_exists(df, [name], overwrite=overwrite)

    df = df.copy()
    cut_off = (sampling_frequency / 60) * 100

    df[name] = pd.NA
    df.loc[df[Column.STEPS] >= cut_off, name] = "moderate-vigorous"

    return df.astype({name: "category"})
