import logging
from typing import Any

__all__ = (
    "is_assume_root",
    "check_logger",
    "check_level_name",
    "check_level",
    "check_formatter",
    "str2int",
)

def str2int(level: Any | None = None) -> bool | int: ...
def is_assume_root(logger_name: Any | None) -> bool: ...
def check_logger(logger: logging.Logger | str | None) -> bool: ...
def check_level_name(
    logger_name: Any | None,
) -> bool: ...
def check_level(
    level: Any | None,
) -> bool: ...
def check_formatter(
    format_: Any | None = ...,
) -> bool: ...
