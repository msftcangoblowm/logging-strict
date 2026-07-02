import types

from packaging.version import (
    InvalidVersion,  # type: ignore[import-untyped, import-not-found, unused-ignore]
)
from packaging.version import (
    Version,  # type: ignore[import-untyped, import-not-found, unused-ignore]
)

__all__ = (
    "InvalidVersion",
    "Version",
    "sanitize_tag",
    "get_version",
    "readthedocs_url",
)

_map_release: types.MappingProxyType[str, str]

def _strip_epoch(ver: str) -> tuple[str | None, str]: ...
def _strip_local(ver: str) -> tuple[str | None, str]: ...
def remove_v(ver: str) -> str: ...
def sanitize_tag(ver: str) -> str: ...
def readthedocs_url(package_name: str, ver_: str = "latest") -> str: ...
def get_version(
    ver: str,
    is_use_final: bool = False,
) -> tuple[tuple[int, int, int, str, int], int]: ...
