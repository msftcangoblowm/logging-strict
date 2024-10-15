import contextlib
import logging
from collections.abc import (
    Iterator,
    MutableSequence,
    Sequence,
)
from typing import Any

import attrs

__all__ = ("captureLogs", "captureLogsMany")

def is_assume_root(
    logger_name: Any | None,
) -> bool: ...
def _normalize_level(
    level: Any | None,
) -> str: ...
def _normalize_level_name(
    logger_name: Any | None,
) -> str: ...
def _normalize_logger(
    logger: logging.Logger | str | None,
) -> logging.Logger: ...
def _normalize_formatter(
    format_: Any | None = ...,
) -> logging.Formatter: ...
@attrs.define
class _LoggingWatcher:
    records: MutableSequence[logging.LogRecord] = ...
    output: MutableSequence[str] = ...

    def getHandlerByName(self, name: str) -> type[logging.Handler]: ...
    def getHandlerNames(self) -> frozenset[str]: ...
    def getLevelNo(self, level_name: str) -> int | None: ...

class _CapturingHandler(logging.Handler):
    def __init__(self) -> None: ...
    def flush(self) -> None: ...
    def emit(self, record: logging.LogRecord) -> None: ...

@attrs.define
class _LoggerStoredState:
    level_name: str = ...
    propagate: bool = ...
    handlers: list[type[logging.Handler]] = ...

@contextlib.contextmanager
def captureLogs(
    logger: str | logging.Logger | None = None,
    level: str | int | None = None,
    format_: str | None = ...,
) -> Iterator[_LoggingWatcher]: ...
@contextlib.contextmanager
def captureLogsMany(
    loggers: Sequence[str | logging.Logger] = (),
    levels: Sequence[str | int | None] = (),
    format_: str | None = ...,
) -> Iterator[Sequence[_LoggingWatcher]]: ...
