"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

.. py:data:: __all__
   :type: tuple[str]
   :value: ("MyLogger",)

   Module exports

.. py:data:: g_package_second_party
   :type: str
   :value: "asz"

   Hardcoded package name. Doing this is obsolete, but in context of testing is ok.

"""

from __future__ import annotations

import sys
from pathlib import Path

from .logging_yaml_abc import (
    VERSION_FALLBACK,
    YAML_LOGGING_CONFIG_SUFFIX,
    LoggingYamlType,
)

if sys.version_info >= (3, 9):  # pragma: no cover
    from collections.abc import Callable
else:  # pragma: no cover
    from typing import Callable

__all__ = ("MyLogger",)

g_package_second_party = "asz"


def file_stem(
    genre: str | None = "mp",
    version: str | None = VERSION_FALLBACK,
    flavor: str | None = g_package_second_party,
) -> str:
    """Test implementation of file_stem."""
    return f"{genre}_{version}_{flavor}"


def file_name(
    category: str | None = "worker",
    genre: str | None = "mp",
    version: str | None = VERSION_FALLBACK,
    flavor: str | None = g_package_second_party,
) -> str:
    """Test implementation of file_name."""
    stem = file_stem(genre=genre, version=version, flavor=flavor)

    return f"{stem}.{category}{YAML_LOGGING_CONFIG_SUFFIX}"


class MyLogger(LoggingYamlType):
    """A basic implementation

    .. py:attribute:: suffixes
       :type: str
       :value: ".my_logger"

       Nonsense logging YAML config file suffixes

    """

    suffixes = ".my_logger"

    def __init__(self, package_name: str, func: Callable[[str], Path]) -> None:
        """Mock class constructor"""
        super().__init__()
        self._package = package_name
        self.func = func

    @property
    def file_stem(self) -> str:
        """Test implementation of property file_stem."""
        return file_stem()

    @property
    def file_name(self) -> str:
        """Test implementation of property file_name."""
        return file_name()

    @property
    def package(self) -> str:
        """Test implementation of property package. Subfolder relative
        path to where package resources are extracted."""
        return self._package

    @property
    def dest_folder(self) -> Path:  # pragma: no cover
        """Package resource destination folder Path"""
        return self.func(self.package)

    def extract(
        self,
        path_relative_package_dir: Path | str | None = "",
    ) -> str:  # pragma: no cover
        """Nonsense package resource extract implementation."""
        return f"relativepath/{self.file_name}"
