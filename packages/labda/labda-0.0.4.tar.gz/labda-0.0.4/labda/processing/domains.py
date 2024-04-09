import pandas as pd

from ..utils import columns_not_exists

# TODO: Possibility to specify if point should be INSIDE or OUTSIDE the domain. Maybe?
# TODO: Get domains


def detect_domains(
    df: pd.DataFrame,
    domains: pd.DataFrame,
    *,
    overwrite: bool = False,
) -> pd.DataFrame:
    df = df.copy()
    unique_domains = domains.groupby("domain")

    for domain in unique_domains:
        name = f"domain_{domain[0]}"

        columns_not_exists(df, [name], overwrite=overwrite)

        domain_df = domain[1]
        df[name] = False

        for interval in domain_df.itertuples():
            df.loc[
                (df.index >= interval.start) & (df.index <= interval.end),
                name,
            ] = True

    return df
