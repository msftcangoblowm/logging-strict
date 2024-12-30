import sys
from pathlib import Path
from typing import Any

from .constants import LoggingConfigCategory
from .logging_yaml_abc import LoggingYamlType

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

__all__ = (
    "LoggingConfigYaml",
    "ui_yaml_curated",
    "setup_ui_other",
    "worker_yaml_curated",
    "setup_worker_other",
    "LoggingState",
)

def cb_true(x: Any) -> bool: ...

class LoggingConfigYaml(LoggingYamlType):
    suffixes: str = ...

    def __init__(
        self,
        package_name: str,
        package_data_folder_start: str,
        category: LoggingConfigCategory | str | Any | None,
        genre: str | None = None,
        flavor: str | None = None,
        version_no: Any | None = ...,
    ) -> None: ...
    @property
    def file_stem(self) -> str: ...
    @property
    def category(self) -> str: ...
    @property
    def genre(self) -> str | None: ...
    @property
    def flavor(self) -> str | None: ...
    @property
    def version(self) -> str: ...
    @version.setter
    def version(self, val: Any) -> None: ...
    @property
    def file_suffix(self) -> str: ...
    @property
    def file_name(self) -> str: ...
    @property
    def package(self) -> str: ...
    @package.setter
    def package(self, val: Any) -> None: ...
    @property
    def dest_folder(self) -> Path: ...
    def extract(
        self,
        path_relative_package_dir: Path | str | None = "",
    ) -> str: ...

def setup_ui_other(
    package_name: str,
    genre: str,
    flavor: str,
    version_no: Any = ...,
    package_start_relative_folder: Path | str | None = "",
    logger_package_name: str | None = None,
) -> None: ...
def ui_yaml_curated(
    genre: str,
    flavor: str,
    version_no: Any | None = ...,
    package_start_relative_folder: Path | str | None = "",
    logger_package_name: str | None = None,
) -> None: ...
def worker_yaml_curated(
    genre: Any | None = "mp",
    flavor: Any | None = "asz",
    version_no: Any | None = ...,
    package_start_relative_folder: Path | str | None = "",
    logger_package_name: str | None = None,
) -> str: ...
def setup_worker_other(
    package_name: str,
    package_data_folder_start: str,
    genre: str,
    flavor: str,
    version_no: Any | None = ...,
    package_start_relative_folder: Path | str | None = "",
    logger_package_name: str | None = None,
) -> str: ...

class LoggingState:
    __instance: Self | None = None

    def __new__(cls, is_state_app: Any | None = False) -> Self: ...
    @property
    def is_state_app(self) -> bool: ...
    @is_state_app.setter
    def is_state_app(self, is_state_app: Any) -> None: ...
