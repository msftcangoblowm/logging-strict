from collections.abc import Callable
from pathlib import Path
from typing import (
    ClassVar,
    Final,
)

from .logging_yaml_abc import LoggingYamlType

__all__ = ("MyLogger",)

g_package_second_party: Final[str]

def file_stem(
    genre: str | None = "mp",
    version: str | None = ...,
    flavor: str | None = ...,
) -> str: ...
def file_name(
    category: str | None = "worker",
    genre: str | None = "mp",
    version: str | None = ...,
    flavor: str | None = ...,
) -> str: ...

class MyLogger(LoggingYamlType):
    suffixes: ClassVar[str] = ".my_logger"
    _package: str
    func: Callable[[str], Path]

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

    # Only to satisfy ABC
    @property
    def version(self) -> str | None: ...
    @property
    def genre(self) -> str | None: ...
    @property
    def flavor(self) -> str | None: ...
    @property
    def category(self) -> str | None: ...
