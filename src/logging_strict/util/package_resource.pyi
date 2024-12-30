import logging
from collections.abc import (
    Callable,
    Iterator,
)
from importlib.abc import Traversable
from pathlib import Path
from typing import (
    Protocol,
    runtime_checkable,
)

__all__ = (
    "filter_by_suffix",
    "filter_by_file_stem",
    "PackageResource",
    "PartSuffix",
    "PartStem",
)

is_module_debug: bool
g_module: str
_LOGGER: logging.Logger

def _extract_folder(package: str) -> str: ...
def _get_package_data_folder(dotted_path: str) -> Traversable | None: ...
def _to_package_case(val: str) -> str: ...
def check_folder(
    x: Traversable,
    cb_suffix: Callable[[str], bool] | None = None,
    cb_file_stem: Callable[[str], bool] | None = None,
) -> Iterator[Traversable]: ...
def filter_by_file_stem(
    expected_file_name: str,
    test_file_name: str,
) -> bool: ...
def filter_by_suffix(
    expected_suffix: str | tuple[str, ...],
    test_suffix: str,
) -> bool: ...
def is_package_exists(package_name: str) -> bool: ...
def match_file(
    y: Traversable,
    /,
    *,
    cb_suffix: Callable[[str], bool] | None = None,
    cb_file_stem: Callable[[str], bool] | None = None,
) -> bool: ...
def msg_stem(file_name: str) -> str: ...
def walk_tree_folders(
    traversable_root: Traversable,
) -> Iterator[Traversable]: ...
@runtime_checkable
class PartSuffix(Protocol):
    def __call__(
        fakeSelf,
        expected_suffix: str | tuple[str, ...],
        test_suffix: str,
    ) -> bool: ...

@runtime_checkable
class PartStem(Protocol):
    def __call__(
        fakeSelf,
        file_expected: str,
        test_file_stem: str,
    ) -> bool: ...

class PackageResource:
    def __init__(
        self,
        package: str,
        package_data_folder_start: str,
    ) -> None: ...
    @property
    def package(self) -> str: ...
    @property
    def package_data_folder_start(self) -> str: ...
    def path_relative(
        self,
        y: Path,
        /,
        *,
        path_relative_package_dir: str | Path | None = None,
        parent_count: int | None = None,
    ) -> Path: ...
    def get_parent_paths(
        self,
        *,
        cb_suffix: Callable[[str], bool] | None = None,
        cb_file_stem: Callable[[str], bool] | None = None,
        path_relative_package_dir: str | Path | None = None,
        parent_count: int | None = 1,
    ) -> dict[str, list[str]]: ...
    def package_data_folders(
        self,
        *,
        cb_suffix: Callable[[str], bool] | None = None,
        cb_file_stem: Callable[[str], bool] | None = None,
        path_relative_package_dir: Path | str | None = None,
    ) -> Iterator[Traversable]: ...
    def resource_extract(
        self,
        base_folder_generator: Iterator[Traversable],
        path_dest: Path | str,
        /,
        cb_suffix: Callable[[str], bool] | None = None,
        cb_file_stem: Callable[[str], bool] | None = None,
        is_overwrite: bool | None = False,
        as_user: bool | None = False,
    ) -> Iterator[Path]: ...
    def cache_extract(
        self,
        base_folder_generator: Iterator[Traversable],
        /,
        cb_suffix: Callable[[str], bool] | None = None,
        cb_file_stem: Callable[[str], bool] | None = None,
        is_overwrite: bool | None = False,
    ) -> Iterator[Path]: ...
