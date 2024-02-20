from __future__ import annotations

import abc
import sys
from pathlib import Path
from typing import (
    Any,
    Optional,
)

if sys.version_info >= (3, 8):  # pragma: no cover
    from typing import Final
else:  # pragma: no cover
    from typing_extensions import Final

if sys.version_info >= (3, 9):  # pragma: no cover
    from collections.abc import Iterator
else:  # pragma: no cover
    from typing import Iterator

__all__: Final[tuple[str, str, str]]

YAML_LOGGING_CONFIG_SUFFIX: Final[str]
PATTERN_DEFAULT: Final[str]

def setup_logging_yaml(path_yaml: Any) -> None: ...
def as_str(package_name: str, file_name: str) -> str: ...

VERSION_FALLBACK: str

class LoggingYamlType(abc.ABC):
    @staticmethod
    def get_version(val: Any) -> str: ...
    @classmethod
    def pattern(
        cls,
        category: Optional[str] = None,
        genre: Optional[str] = None,
        flavor: Optional[str] = None,
        version: Optional[str] = VERSION_FALLBACK,
    ) -> str: ...
    def iter_yamls(
        self,
        path_dir: Path,
        category: Optional[str] = None,
        genre: Optional[str] = None,
        flavor: Optional[str] = None,
        version: Optional[str] = VERSION_FALLBACK,
    ) -> Iterator[Path]: ...
    @classmethod
    def __subclasshook__(cls, C: Any) -> bool: ...
    @property
    @abc.abstractmethod
    def file_stem(self) -> str: ...
    @property
    @abc.abstractmethod
    def file_name(self) -> str: ...
    @property
    @abc.abstractmethod
    def package(self) -> str: ...
    @property
    @abc.abstractmethod
    def dest_folder(self) -> Path: ...
    @abc.abstractmethod
    def extract(
        self,
        path_relative_package_dir: Path | str | None = "",
    ) -> str: ...
    def as_str(self) -> str: ...
    def setup(self, str_yaml: str) -> None: ...
