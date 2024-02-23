from __future__ import annotations

import sys
from pathlib import Path

from .logging_yaml_abc import (
    VERSION_FALLBACK,
    LoggingYamlType,
)

if sys.version_info >= (3, 8):
    from typing import Final
else:
    from typing_extensions import Final

if sys.version_info >= (3, 9):
    from collections.abc import Callable
else:
    from typing import Callable

__all__: Final[tuple[str]]

g_package_second_party: Final[str]

def file_stem(
    genre: str | None = "mp",
    version: str | None = VERSION_FALLBACK,
    flavor: str | None = g_package_second_party,
) -> str: ...
def file_name(
    category: str | None = "worker",
    genre: str | None = "mp",
    version: str | None = VERSION_FALLBACK,
    flavor: str | None = g_package_second_party,
) -> str: ...

class MyLogger(LoggingYamlType):
    suffixes: str = ".my_logger"

    def __init__(self, package_name: str, func: Callable[[str], Path]) -> None: ...
    @property
    def file_stem(self) -> str: ...
    @property
    def file_name(self) -> str: ...
    @property
    def package(self) -> str: ...
    @property
    def dest_folder(self) -> Path: ...
    def extract(
        self,
        path_relative_package_dir: Path | str | None = "",
    ) -> str: ...
