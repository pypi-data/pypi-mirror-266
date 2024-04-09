import secrets
from functools import partial
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

from ..parallel import parallel_processing
from .subject import Subject


def _to_parquet_with_path(subject, path, overwrite):
    subject_path = path / f"{subject.metadata.id}.parquet"
    return Subject.to_parquet(subject, path=subject_path, overwrite=overwrite)


class Collection(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: secrets.token_hex(4))
    subjects: list[Subject] = Field(default_factory=list)

    def __repr__(self):
        subjects_repr = ", ".join([p.metadata.id for p in self.subjects])  # type: ignore
        return f"Collection(id={self.id}, subjects=[{subjects_repr}])"

    def add_subject(self, subject: Subject):
        subjects_ids = [s.metadata.id for s in self.subjects]

        if subject.metadata.id in subjects_ids:
            raise ValueError(
                f"Subject with id '{subject.metadata.id}' already exists in collection."
            )

        subject.collection = self.id  # type: ignore
        self.subjects.append(subject)  # type: ignore

    def get_subject(self, id: str) -> Subject:
        for subject in self.subjects:
            if subject.metadata.id == id:
                return subject
        raise ValueError(f"Subject with id '{id}' not found.")

    @classmethod
    def from_folder(cls, path: str | Path, id: str | None = None) -> "Collection":
        if isinstance(path, str):
            path = Path(path)

        files = list(path.glob("*.parquet"))

        if not files:
            raise ValueError(f"No parquet files found in '{path}'.")

        subjects = [Subject.from_parquet(file) for file in files]
        return cls(id=id, subjects=subjects)

    def to_folder(
        self,
        path: str | Path,
        *,
        parallel: bool = True,
        n_cores: int | str = "max",
        overwrite: bool = False,
    ):
        if isinstance(path, str):
            path = Path(path)

        path.mkdir(parents=True, exist_ok=True)

        if not path.is_dir():
            raise ValueError(f"'{path}' is not a valid directory.")

        if parallel:
            self.subjects = parallel_processing(
                partial(_to_parquet_with_path, path=path, overwrite=overwrite),
                self.subjects,
                n_cores,
            )
        else:
            for subject in self.subjects:
                subject.to_parquet(
                    path / f"{subject.metadata.id}.parquet", overwrite=overwrite
                )

    def detect_trips(
        self,
        *,
        parallel: bool = True,
        n_cores: int | str = "max",
        **kwargs,
    ):
        if parallel:
            self.subjects = parallel_processing(
                Subject.detect_trips,
                self.subjects,
                n_cores,
                **kwargs,
            )
        else:
            for subject in self.subjects:
                subject.detect_trips(**kwargs)

    def detect_activity_intensity(
        self,
        *,
        parallel: bool = True,
        n_cores: int | str = "max",
        **kwargs,
    ) -> None:
        if parallel:
            self.subjects = parallel_processing(
                Subject.detect_activity_intensity,
                self.subjects,
                n_cores,
                **kwargs,
            )
        else:
            for subject in self.subjects:
                subject.detect_activity_intensity(**kwargs)

    # TODO: Rework whole consistency check
    # TODO: Add also check columns consistency
    # TODO: Check if collection is not empty.
    def _check_consistency(self, attribute, error_message):
        # TODO: Add docstring, better name for method
        values = [getattr(subject.metadata, attribute) for subject in self.subjects]
        unique = set(values)

        if len(unique) != 1:
            print(f"{error_message}: {unique}")

    def _check_consistent_sampling_frequencies(self):
        self._check_consistency(
            "sampling_frequency", "Sampling frequencies are not consistent"
        )

    def _check_consistent_crs(self):
        self._check_consistency("crs", "CRS are not consistent")

    def _check_consistent_timezones(self):
        self._check_consistency("timezone", "Timezones are not consistent")

    def check_consistency(self):
        self._check_consistent_sampling_frequencies()
        self._check_consistent_crs()
        self._check_consistent_timezones()

        print("Consistency check finished.")
