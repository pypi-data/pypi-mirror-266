import sys
from pathlib import Path

from loguru import logger

from .structure.subject import Subject


def color_level(record):
    match record["level"].name:
        case "ERROR":
            color = "red"
        case "SUCCESS":
            color = "green"
        case _:
            color = "white"

    return color


def formatter(record):
    color = color_level(record)
    return (
        f"<{color}>"
        + "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}\n"
        + f"</{color}>"
    )


def configure_logger(level: str):
    logger.remove()
    logger.add(
        sys.stderr,
        format=formatter,
        colorize=True,
        level=level,
    )


def success_parsing_log(
    subject: Subject,
    path: Path,
    func: str,
):
    meta = subject.metadata
    sampling_frequency = (
        f"SF: {meta.sampling_frequency}s" if meta.sampling_frequency else ""
    )
    timezone = f", TZ: {meta.timezone}" if meta.timezone else ""
    crs = f", CRS: {meta.crs}" if meta.crs else ""

    logger.success(
        f"{func} | {path} | Parsed {len(subject.df)} records ({sampling_frequency}{timezone}{crs})"
    )
