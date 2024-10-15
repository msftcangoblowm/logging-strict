from collections.abc import Iterator
from enum import Enum
from typing import (
    Any,
    Final,
)

__all__ = (
    "g_app_name",
    "__version_app",
    "__url__",
    "PREFIX_DEFAULT",
    "LoggingConfigCategory",
    "LOG_FORMAT",
    "FALLBACK_LEVEL",
)

g_app_name: Final[str]
PREFIX_DEFAULT: Final[str]

def enum_map_func_get_value(enum_item: type[Enum]) -> Any: ...

class LoggingConfigCategory(Enum):
    WORKER = "worker"
    UI = "app"

    @classmethod
    def categories(cls) -> Iterator[str]: ...

LOG_FORMAT: Final[str]
FALLBACK_LEVEL: Final[str]

LOG_FMT_DETAILED: Final[str]
LOG_FMT_SIMPLE: Final[str]
LOG_LEVEL_WORKER: Final[str]

__version_app: Final[str]
__url__: Final[str]
