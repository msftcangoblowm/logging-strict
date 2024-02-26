from __future__ import annotations

import contextlib
import logging
import sys
from typing import Any

import attrs

if sys.version_info >= (3, 8):  # pragma: no cover
    from collections.abc import (
        MutableSequence,
        Sequence,
    )
    from typing import Final
else:
    from typing import (
        MutableSequence,
        Sequence,
    )

    from typing_extensions import Final

if sys.version_info >= (3, 9):  # pragma: no cover
    from collections.abc import Iterator
else:  # pragma: no cover
    from typing import Iterator

from ..constants import (
    FALLBACK_LEVEL,
    LOG_FORMAT,
)

__all__: Final[tuple[str, str]]

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
    format_: Any | None = LOG_FORMAT,
) -> logging.Formatter: ...
@attrs.define
class _LoggingWatcher:
    """Replaces collections.namedtuple"""

    records: MutableSequence[logging.LogRecord] = attrs.field(
        factory=list,
        kw_only=False,
        validator=attrs.validators.deep_iterable(
            member_validator=attrs.validators.instance_of(logging.LogRecord),
            iterable_validator=attrs.validators.instance_of(list),
        ),
    )
    output: MutableSequence[str] = attrs.field(
        factory=list,
        kw_only=False,
        validator=attrs.validators.deep_iterable(
            member_validator=attrs.validators.instance_of(str),
            iterable_validator=attrs.validators.instance_of(list),
        ),
    )

    def getHandlerByName(self, name: str) -> type[logging.Handler]: ...
    def getHandlerNames(self) -> frozenset[str]: ...
    def getLevelNo(self, level_name: str) -> int | None: ...

class _CapturingHandler(logging.Handler):
    def __init__(self) -> None: ...
    def flush(self) -> None: ...
    def emit(self, record: logging.LogRecord) -> None: ...

@attrs.define
class _LoggerStoredState:
    level_name: str = attrs.field(kw_only=False)
    propagate: bool = attrs.field(kw_only=False)
    handlers: list[type[logging.Handler]] = attrs.field(
        kw_only=False,
        factory=list,
        validator=attrs.validators.deep_iterable(
            member_validator=attrs.validators.instance_of(logging.Handler),
            iterable_validator=attrs.validators.instance_of(list),
        ),
    )

@contextlib.contextmanager
def captureLogs(
    logger: str | logging.Logger | None = None,
    level: str | int | None = None,
    format_: str | None = LOG_FORMAT,
) -> Iterator[_LoggingWatcher]: ...
@contextlib.contextmanager
def captureLogsMany(
    loggers: Sequence[str | logging.Logger] = (),
    levels: Sequence[str | int | None] = (),
    format_: str | None = LOG_FORMAT,
) -> Iterator[Sequence[_LoggingWatcher]]: ...
