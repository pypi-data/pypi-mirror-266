from datetime import timedelta
from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    # This is a workaround to avoid circular imports.
    # TODO: Is there a better way to do this?
    from .collection import Collection

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from pydantic import BaseModel, Field

from ..expanders import (
    add_acceleration,
    add_direction,
    add_distance,
    add_speed,
    add_timedelta,
)
from ..processing import detect_domains
from ..processing.accelerometer import detect_activity_intensity, detect_wear
from ..processing.spatial import detect_transportation, detect_trips, get_timeline
from ..structure.resampling import upsample
from ..utils import columns_exists, columns_not_exists, convert_to_geodataframe
from ..visualisation.spatial import plot
from .validation.domains import SCHEMA as DOMAINS_SCHEMA
from .validation.subject import SCHEMA, Column


class Vendor(StrEnum):
    ACTIGRAPH = "ActiGraph"
    XIAOMI = "Xiaomi"
    SENS = "SENS"
    GARMIN = "Garmin"
    QSTARZ = "Qstarz"
    GGIR = "GGIR"
    SENSECAP = "SenseCap"
    ANDROID = "Android"
    IOS = "iOS"


class Sensor(BaseModel):
    id: str
    serial_number: str | None = None
    model: str | None = None
    vendor: Vendor | None = None
    firmware_version: str | None = None
    extra: dict[str, Any] | None = None

    class Config:
        coerce_numbers_to_str = True


class Metadata(BaseModel):
    id: str
    sensor: list[Sensor] = Field(default_factory=list)
    sampling_frequency: float = Field(ge=0, description="Sampling frequency in seconds")
    crs: str | None = None
    timezone: str | None = None

    class Config:
        coerce_numbers_to_str = True


class Subject(BaseModel):
    metadata: Metadata
    collection: Optional["Collection"] = None
    df: pd.DataFrame
    timeline: pd.DataFrame | None = None

    # TODO: Add check for not empty dataframe.

    class Config:
        arbitrary_types_allowed = True

    def __str__(self):
        return str(f"{self.metadata}\n{self.df}")

    @property
    def domains(self):
        # TODO: Implement this property.
        raise NotImplementedError("This method is not implemented yet.")

    def to_parquet(
        self,
        path: str | Path,
        *,
        overwrite: bool = False,
    ) -> None:
        if isinstance(path, str):
            path = Path(path)

        if path.exists() and not overwrite:
            raise FileExistsError(
                f"The file '{path}' already exists. If you want to overwrite it, set the 'overwrite' argument to 'True'."
            )
        else:
            path.parent.mkdir(parents=True, exist_ok=True)

        custom_metadata = {"labda".encode(): self.metadata.model_dump_json().encode()}
        self.validate()
        table = pa.Table.from_pandas(self.df)

        existing_metadata = table.schema.metadata
        combined_meta = {**custom_metadata, **existing_metadata}

        table = table.replace_schema_metadata(combined_meta)
        pq.write_table(table, path)

    @classmethod
    def from_parquet(cls, path: str | Path) -> "Subject":
        if isinstance(path, str):
            path = Path(path)

        table = pq.read_table(path)
        df = table.to_pandas()
        custom_metadata = Metadata.model_validate_json(
            table.schema.metadata["labda".encode()]
        )
        cls = cls(metadata=custom_metadata, df=df)
        cls.validate()

        return cls

    def validate(
        self,
        *,
        extra_columns: bool = False,
    ):
        if self.df.empty:
            raise ValueError("DataFrame is empty.")

        self.df = SCHEMA.validate(self.df)

        # Order columns as defined in Column
        records_columns = [col.value for col in Column]
        ordered_columns = [col for col in records_columns if col in self.df.columns]

        # Append extra columns that are not in Column at the end, alphabetically
        if extra_columns:
            extra = sorted(set(self.df.columns) - set(records_columns))
            ordered_columns.extend(extra)

        self.df = self.df[ordered_columns]

    def add_timedelta(
        self,
        *,
        name: str = Column.TIMEDELTA,
        overwrite: bool = False,
    ):
        self.df = add_timedelta(self.df, name=name, overwrite=overwrite)

    def add_distance(
        self,
        *,
        name: str = Column.DISTANCE,
        overwrite: bool = False,
    ):
        self.df = add_distance(
            self.df, crs=self.metadata.crs, name=name, overwrite=overwrite
        )

    def add_speed(
        self,
        *,
        name: str = Column.SPEED,
        overwrite: bool = False,
    ):
        self.df = add_speed(
            self.df, crs=self.metadata.crs, name=name, overwrite=overwrite
        )

    def add_acceleration(
        self,
        *,
        name: str = Column.ACCELERATION,
        overwrite: bool = False,
    ):
        self.df = add_acceleration(
            self.df, crs=self.metadata.crs, name=name, overwrite=overwrite
        )

    def add_direction(
        self,
        *,
        name: str = Column.DIRECTION,
        overwrite: bool = False,
    ):
        self.df = add_direction(self.df, name=name, overwrite=overwrite)

    def detect_trips(
        self,
        cut_points: dict[str, Any] | None = None,
        *,
        gap_duration: timedelta,
        stop_radius: int | float,
        stop_duration: timedelta,
        window: int | None = None,
        pause_radius: int | float | None = None,
        pause_duration: timedelta | None = None,
        min_duration: timedelta | None = None,
        min_length: int | float | None = None,
        min_distance: int | float | None = None,
        max_speed: int | float | None = None,
        indoor_limit: float | None = None,
        overwrite: bool = False,
    ) -> None:
        if not self.metadata.crs:
            raise ValueError("Records object does not have a CRS defined.")

        self.df = detect_trips(
            self.df,
            crs=self.metadata.crs,
            sampling_frequency=self.metadata.sampling_frequency,
            overwrite=overwrite,
            gap_duration=gap_duration,
            stop_radius=stop_radius,
            stop_duration=stop_duration,
            pause_radius=pause_radius,
            pause_duration=pause_duration,
            min_duration=min_duration,
            min_length=min_length,
            min_distance=min_distance,
            max_speed=max_speed,
            indoor_limit=indoor_limit,
        )

        if cut_points:
            self.df = detect_transportation(
                self.df,
                self.metadata.crs,
                cut_points,
                window=window,
                overwrite=overwrite,
            )

        if not overwrite and self.timeline:
            raise ValueError("Timeline already exists. Set 'overwrite' to 'True'.")
        else:
            self.timeline = get_timeline(self.df, crs=self.metadata.crs)

    def detect_domains(
        self,
        domains: pd.DataFrame,
        *,
        overwrite: bool = False,
    ) -> None:
        domains = DOMAINS_SCHEMA.validate(domains)
        subject_domains = domains[
            (domains[Column.SUBJECT_ID] == self.metadata.id)
            | (domains[Column.SUBJECT_ID].isna())
        ]
        self.df = detect_domains(self.df, subject_domains, overwrite=overwrite)

    def detect_activity_intensity(
        self,
        cut_points: dict[str, Any],
        *,
        overwrite: bool = False,
    ) -> None:
        self.df = detect_activity_intensity(
            self.df,
            cut_points,
            self.metadata.sampling_frequency,
            overwrite=overwrite,
        )

    def detect_wear(
        self,
        min_duration: timedelta,
        interruption_duration: timedelta,
        *,
        overwrite: bool = False,
    ) -> None:
        self.df = detect_wear(
            self.df,
            self.metadata.sampling_frequency,
            min_duration,
            interruption_duration=interruption_duration,
            overwrite=overwrite,
        )

    def upsample(
        self,
        sampling_frequency: float,
        *,
        mapper: list[dict[str, Any]] | None = None,
    ) -> None:
        self.df = upsample(
            self.df, self.metadata.sampling_frequency, sampling_frequency, mapper
        )
        self.metadata.sampling_frequency = sampling_frequency

    def plot(self, kind: str = "gps") -> Any:
        match kind:
            case "timeline":
                if isinstance(self.timeline, pd.DataFrame):
                    df = self.timeline
                else:
                    raise ValueError("Timeline does not exist. Run 'detect_trips'.")
            case "gps":
                df = self.df
            case _:
                raise ValueError(f"Kind '{kind}' not supported.")

        return plot(df, kind, crs=self.metadata.crs)
