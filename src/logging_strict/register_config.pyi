from collections.abc import Sequence
from pathlib import Path
from typing import (
    Any,
    Final,
)

import strictyaml as s

from .constants import LoggingConfigCategory

CONFIG_STEM: Final[str]
CONFIG_SUFFIX: Final[str]
REGEX_REL_PATH: Final[str]

_category_values: s.scalar.Enum
_item_map: s.compound.MapCombined
_file_map: s.compound.Map
_schema: s.compound.Seq

class ExtractorLoggingConfig:
    __slots__ = (
        "_package_name",
        "_patch_extract_folder",
        "_path_extraction_dir",
        "_is_test_file",
        "_path_extracted_db",
        "_logging_config_yaml_str",
        "_registry",
        "_logging_config_yaml_relpath",
    )
    def __init__(
        self,
        package_name: str,
        path_alternative_dest_folder: Path | None = None,
        is_test_file: bool | None = False,
    ) -> None: ...
    def __repr__(self) -> str: ...
    @staticmethod
    def clean_package_name(val: Any) -> str | None: ...
    @property
    def package_name(self) -> str: ...
    @package_name.setter
    def package_name(self, val: Any) -> None: ...
    @property
    def path_extracted_db(self) -> Path | None: ...
    @property
    def is_test_file(self) -> bool: ...
    @property
    def logging_config_yaml_str(self) -> str | dict[str, Any] | None: ...
    @property
    def logging_config_yaml_relpath(self) -> Path | None: ...
    def extract_db(self) -> None: ...
    def get_db(self, path_extracted_db: Path | None = None) -> None: ...
    def query_db(
        self,
        category: LoggingConfigCategory | str | Any | None,
        genre: str | None = None,
        flavor: str | None = None,
        version_no: str | None = ...,
        logger_package_name: str | None = None,
        is_skip_setup: bool | None = True,
    ) -> str | None: ...
