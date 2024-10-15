import abc
from collections.abc import Iterator
from pathlib import Path
from typing import (
    Any,
    Final,
)

__all__ = ("LoggingYamlType", "YAML_LOGGING_CONFIG_SUFFIX", "setup_logging_yaml")

YAML_LOGGING_CONFIG_SUFFIX: Final[str]
PATTERN_DEFAULT: Final[str]
VERSION_FALLBACK: str

def setup_logging_yaml(path_yaml: Any) -> None: ...
def as_str(package_name: str, file_name: str) -> str: ...

class LoggingYamlType(abc.ABC):
    @staticmethod
    def get_version(val: Any) -> str: ...
    @classmethod
    def pattern(
        cls,
        category: str | None = None,
        genre: str | None = None,
        flavor: str | None = None,
        version: str | None = ...,
    ) -> str: ...
    def iter_yamls(
        self,
        path_dir: Path,
        category: str | None = None,
        genre: str | None = None,
        flavor: str | None = None,
        version: str | None = ...,
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
