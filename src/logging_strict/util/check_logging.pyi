from __future__ import annotations

import logging
import sys
from typing import (
    Any,
    Optional,
)

from ..constants import LOG_FORMAT

if sys.version_info >= (3, 8):
    from typing import Final
else:
    from typing_extensions import Final

__all__: Final[tuple[str, str, str, str, str, str]]

def str2int(level: Optional[Any] = None) -> bool | int: ...
def is_assume_root(logger_name: Optional[Any]) -> bool: ...
def check_logger(logger: logging.Logger | str | None) -> bool: ...
def check_level_name(
    logger_name: Optional[Any],
) -> bool: ...
def check_level(
    level: Optional[Any],
) -> bool: ...
def check_formatter(
    format_: Optional[Any] = LOG_FORMAT,
) -> bool: ...
