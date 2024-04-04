from __future__ import annotations

import logging
import sys
from typing import Any

from ..constants import LOG_FORMAT

if sys.version_info >= (3, 8):
    from typing import Final
else:
    from typing_extensions import Final

__all__: Final[tuple[str, str, str, str, str, str]]

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
    format_: Any | None = LOG_FORMAT,
) -> bool: ...
