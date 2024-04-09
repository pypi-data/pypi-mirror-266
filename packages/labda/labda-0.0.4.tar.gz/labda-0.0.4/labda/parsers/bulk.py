from pathlib import Path
from typing import Callable

from ..parallel import parallel_processing, process_obj
from ..structure import Collection

# TODO: Add bulk parsing with linkage file


def bulk_parser(
    folder: str | Path,
    parser: Callable,
    id: str | None = None,
    parallel: bool = True,
    n_cores: int | str = "max",
    **kwargs,
):
    if isinstance(folder, str):
        folder = Path(folder)

    if not folder.is_dir():
        raise ValueError(f"'{folder}' is not a valid folder.")

    files = list(Path(folder).glob("*"))

    if id is None:
        id = folder.name

    if parallel:
        results = parallel_processing(parser, files, n_cores, **kwargs)
    else:
        results = [process_obj(file, parser, **kwargs) for file in files]

    # Remove None values from results
    results = list(filter(None, results))

    collection = Collection(id=id, subjects=results)

    return collection
