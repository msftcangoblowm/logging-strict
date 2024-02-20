from __future__ import annotations

import sys
from pathlib import Path

from .logging_yaml_abc import (
    YAML_LOGGING_CONFIG_SUFFIX,
    LoggingYamlType,
)

if sys.version_info >= (3, 8):
    from typing import Final
else:
    from typing_extensions import Final

if sys.version_info >= (3, 9):  # pragma: no cover
    from collections.abc import Callable
else:  # pragma: no cover
    from typing import Callable

__all__: Final[tuple[str]] = ("MyLogger",)

g_package_second_party: Final[str] = "asz"


def file_stem(
    genre: str | None = "mp",
    version: str | None = "1",
    flavor: str | None = g_package_second_party,
) -> str:
    return f"{genre}_{version}_{flavor}"


def file_name(
    category: str | None = "worker",
    genre: str | None = "mp",
    version: str | None = "1",
    flavor: str | None = g_package_second_party,
) -> str:
    stem = file_stem(genre=genre, version=version, flavor=flavor)

    return f"{stem}.{category}{YAML_LOGGING_CONFIG_SUFFIX}"


class MyLogger(LoggingYamlType):
    """A basic implementation"""

    suffixes: str = ".my_logger"

    def __init__(self, package_name: str, func: Callable[[str], Path]) -> None:
        super().__init__()
        self._package = package_name
        self.func = func

    @property
    def file_stem(self) -> str:
        return file_stem()

    @property
    def file_name(self) -> str:
        return file_name()

    @property
    def package(self) -> str:
        return self._package

    @property
    def dest_folder(self) -> Path:  # pragma: no cover
        return self.func(self.package)

    def extract(
        self,
        path_relative_package_dir: Path | str | None = "",
    ) -> str:  # pragma: no cover
        return f"relativepath/{self.file_name}"
