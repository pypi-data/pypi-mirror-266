import numpy as np
import pandas as pd

from ..structure.validation.subject import Column
from ..utils import columns_exists, columns_not_exists


def add_counts_vector_magnitude(
    df: pd.DataFrame,
    *,
    name: str = Column.VM_COUNTS,
    overwrite: bool = False,
) -> pd.DataFrame:
    counts_cols = [
        Column.VERTICAL_COUNTS,
        Column.HORIZONTAL_COUNTS,
        Column.PERPENDICULAR_COUNTS,
    ]

    columns_exists(df, counts_cols)  # type: ignore
    columns_not_exists(df, [name], overwrite=overwrite)

    df = df.copy()
    df[name] = np.linalg.norm(
        df[counts_cols].astype(float),
        axis=1,
    )

    return df
