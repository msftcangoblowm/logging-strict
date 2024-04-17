import sys
import types
from enum import Enum
from typing import Any

if sys.version_info >= (3, 8):  # pragma: no cover
    from typing import Final
else:  # pragma: no cover
    from typing_extensions import Final

if sys.version_info >= (3, 9):  # pragma: no cover
    from collections.abc import Iterator
else:  # pragma: no cover
    from typing import Iterator

__all__: Final[tuple[str, str, str, str, str, str, str]]

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
