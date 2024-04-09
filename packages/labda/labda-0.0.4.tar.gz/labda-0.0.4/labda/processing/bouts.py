from datetime import timedelta

import pandas as pd

from ..utils import columns_not_exists, get_unique_column_name


def _get_duration(g):
    return g.index[-1] - g.index[0]


def get_bouts(
    df: pd.DataFrame,
    column: str,
    sampling_frequency: float,
    min_duration: timedelta,
    min_value: float,
    max_value: float,
    *,
    interruption_duration: timedelta | None = None,
    name: str = "bout",
    overwrite: bool = False,
) -> pd.DataFrame:
    columns_not_exists(df, [name], overwrite=overwrite)

    if interruption_duration and min_duration <= interruption_duration:
        raise ValueError(
            "The interruption duration must be less than the bout duration"
        )

    bout = get_unique_column_name(df)
    bout_id = get_unique_column_name(df)
    possibly_bout = get_unique_column_name(df)

    temp_df = df[[column]].copy()
    temp_df = temp_df.resample(f"{sampling_frequency}s").asfreq()
    # TODO: Bouts should be more based on column with True/False values only, so user needs to preprocess the data.
    # TODO: So it should be this column as input, not the min/max values.
    temp_df[bout] = (temp_df[column] >= min_value) & (temp_df[column] <= max_value)

    temp_df[bout_id] = (temp_df[bout] != temp_df[bout].shift(1)).cumsum()

    if interruption_duration:
        # All rows are possible bouts
        temp_df[possibly_bout] = True

        # Calculate the duration of the interruptions
        interruption = (
            temp_df[temp_df[bout] == False]
            .groupby(bout_id)
            .apply(_get_duration, include_groups=False)
        )

        # Get consecutive interruptions where the duration is over the specific time
        interruption_rows = interruption[interruption >= interruption_duration].index

        # Set possibility of bout to False because interruption is too long
        temp_df.loc[temp_df[bout_id].isin(interruption_rows), possibly_bout] = False

        # Recreate the bout_id with the interruptions
        temp_df[bout_id] = (
            temp_df[possibly_bout] != temp_df[possibly_bout].shift(1)
        ).cumsum()
    else:
        temp_df[possibly_bout] = temp_df[bout]

    # Create the final column with the bouts. Default to False
    temp_df[name] = False

    # Calculate the duration of the bouts
    bout_duration = (
        temp_df[temp_df[possibly_bout]]
        .groupby(bout_id)
        .apply(_get_duration, include_groups=False)
    )

    # Get consecutive bouts where the duration is over the specific time
    bout_rows = bout_duration[bout_duration >= min_duration].index

    # Set bout to True for the rows where the duration is over the specific time
    temp_df.loc[temp_df[bout_id].isin(bout_rows), name] = True

    df = df.join(temp_df[[name]], how="left")

    return df
