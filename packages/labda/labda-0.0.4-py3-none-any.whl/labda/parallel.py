import multiprocessing as mp
from functools import partial
from typing import Any, Callable

from .logging import logger
from .structure.subject import Subject


def process_obj(obj: Any, func: Callable, **kwargs) -> Any | None:
    try:
        if isinstance(obj, Subject):
            func(obj, **kwargs)
            return obj

        return func(obj, **kwargs)
    except Exception as e:
        logger.error(f"{func.__module__}:{func.__name__} | {obj} | {e}")


def parallel_processing(
    func: Callable,
    objs: list[Any],
    n_cores: int | str = "max",
    **kwargs,
) -> list[Any]:
    max_cores = mp.cpu_count()

    if n_cores == "max":
        n_cores = max_cores
    elif isinstance(n_cores, int) and n_cores > max_cores:
        raise ValueError(f"Maximum number of cores is {max_cores}. Received {n_cores}.")
    else:
        raise ValueError(f"Invalid value for n_cores: {n_cores}.")

    with mp.Pool(n_cores) as pool:
        results = pool.map(
            partial(process_obj, func=func, **kwargs),
            objs,
        )

    return results
