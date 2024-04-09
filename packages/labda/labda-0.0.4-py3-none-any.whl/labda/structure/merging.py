import pandas as pd

from .collection import Collection
from .subject import Metadata, Subject


def _check_duplicate_cols(left: pd.DataFrame, right: pd.DataFrame) -> None:
    duplicate_cols = set(left.columns) & set(right.columns)
    if duplicate_cols:
        raise ValueError(f"Before merging, remove duplicate columns: {duplicate_cols}")


def _check_ids(left: Subject, right: Subject) -> str:
    if left.metadata.id != right.metadata.id:
        raise ValueError(f"IDs do not match: {left.metadata.id} != {right.metadata.id}")

    return left.metadata.id


def _check_sampling_frequency(left: Subject, right: Subject) -> float:
    if left.metadata.sampling_frequency != right.metadata.sampling_frequency:
        raise ValueError(
            f"Sampling frequency mismatch: {left.metadata.sampling_frequency} != {right.metadata.sampling_frequency}"
        )

    return left.metadata.sampling_frequency


def _check_timezones(left: Subject, right: Subject) -> str | None:
    if (
        (left.metadata.timezone)
        and (right.metadata.timezone)
        and left.metadata.timezone != right.metadata.timezone
    ):
        raise ValueError(
            f"Timezone mismatch: {left.metadata.timezone} != {right.metadata.timezone}"
        )

    return left.metadata.timezone or right.metadata.timezone


def _check_crs(left: Subject, right: Subject) -> str | None:
    if (
        (left.metadata.crs)
        and (right.metadata.crs)
        and left.metadata.crs != right.metadata.crs
    ):
        raise ValueError(f"CRS mismatch: {left.metadata.crs} != {right.metadata.crs}")

    return left.metadata.crs or right.metadata.crs


def _get_subjects(collection: Collection) -> list[str]:
    return [subject.metadata.id for subject in collection.subjects]


def merge_subjects(
    left: Subject, right: Subject, how: str = "inner", **kwargs
) -> Subject:
    # TODO: Log not overlapping rows.
    if not isinstance(left, Subject) and not isinstance(right, Subject):
        raise ValueError(f"Unsupported types: {type(left)} and {type(right)}")

    id = _check_ids(left, right)
    sf = _check_sampling_frequency(left, right)
    tz = _check_timezones(left, right)
    crs = _check_crs(left, right)

    metadata = Metadata(
        id=id,
        sensor=left.metadata.sensor + right.metadata.sensor,
        sampling_frequency=sf,
        timezone=tz,
        crs=crs,
    )

    # FIXME: Add suffixes to columns, even if not duplicated
    if not kwargs.get("suffixes"):
        _check_duplicate_cols(left.df, right.df)
    merged = pd.merge(
        left.df, right.df, left_index=True, right_index=True, how=how, **kwargs
    )  # type: ignore

    return Subject(metadata=metadata, df=merged)


def merge_collections(
    left: Collection,
    right: Collection,
    *,
    how: str = "inner",
    keep: bool = False,
    **kwargs,
) -> Collection:
    if not isinstance(left, Collection) and not isinstance(right, Collection):
        raise ValueError(f"Unsupported types: {type(left)} and {type(right)}")

    left_ids = _get_subjects(left)
    right_ids = _get_subjects(right)
    subjects = set(left_ids + right_ids)

    collection = Collection()

    for subject in subjects:
        try:
            left_subject = left.get_subject(subject)
        except Exception:
            left_subject = None

        try:
            right_subject = right.get_subject(subject)
        except Exception:
            right_subject = None

        if left_subject and right_subject:
            merged_subject = merge_subjects(
                left_subject, right_subject, how=how, **kwargs
            )

            if not merged_subject.df.empty:
                collection.add_subject(merged_subject)
            else:
                print(
                    f"Error while merging | {subject} | Merged subject is empty and will be dropped."
                )
        else:
            print(
                f"Error while merging | {subject} | Subject not found in both collections."
            )

            # FIXME: Fix, it is not working
            # FIXME: Suffix to check if exists
            # FIXME: Native pd.merge function adds suffixes to columns with the same name otherwise not (no suffixes and we don't know the origin of the column)
            # TODO: This could be reworked, maybe not needed to do KEEP, just outer join.
            # TODO: Maybe completely remove the keep argument.

            if keep:
                if left_subject:
                    # suffix = kwargs.get("suffixes")
                    # if suffix:
                    #     left_subject.df = left_subject.df.add_suffix(suffix[0])
                    collection.add_subject(left_subject)
                elif right_subject:
                    # suffix = kwargs.get("suffixes")
                    # if suffix:
                    #     right_subject.df = right_subject.df.add_suffix(suffix[1])
                    collection.add_subject(right_subject)

    return collection
