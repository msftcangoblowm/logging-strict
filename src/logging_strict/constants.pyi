import sys
import types
from enum import Enum
from typing import Any

# py38+
if sys.version_info >= (3, 8):  # pragma: no cover
    from typing import Final
else:  # pragma: no cover
    from typing_extensions import Final

if sys.version_info >= (3, 9):  # pragma: no cover
    from collections.abc import Iterator
else:  # pragma: no cover
    from typing import Iterator

# https://github.com/python/typeshed/blob/main/stdlib/logging/config.pyi#L53
# import logging.config._DictConfigArgs
# from typing import Any

__all__: Final[tuple[str, str, str, str, str, str, str, str]]

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
_map_release: types.MappingProxyType[str, str]

def sanitize_tag(ver: str) -> str: ...
def _make_url_from_version(ver_orig: str) -> str: ...
def get_version(
    ver: str,
    is_use_final: bool = False,
) -> tuple[tuple[int, int, int, str, int], int]: ...

__version_app: str
__url__: str
