from __future__ import annotations

from pathlib import Path

from .logging_yaml_abc import (
    YAML_LOGGING_CONFIG_SUFFIX,
    LoggingYamlType,
)

__all__ = ("MyLogger",)

g_package_second_party = "asz"


def file_stem(
    genre: str | None = "mp",
    version: str | None = "1",
    flavor: str | None = g_package_second_party,
) -> str | None:
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

    def __init__(self, package_name, func):
        super().__init__()
        self._package = package_name
        self.func = func

    @property
    def file_stem(self) -> str | None:
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

    def extract(self) -> None:  # pragma: no cover
        pass
