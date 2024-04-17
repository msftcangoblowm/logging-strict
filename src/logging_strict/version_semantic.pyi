import sys
import types

if sys.version_info >= (3, 8):  # pragma: no cover
    from typing import Final
else:  # pragma: no cover
    from typing_extensions import Final

__all__: Final[tuple[str, str, str]]

_map_release: types.MappingProxyType[str, str]

def sanitize_tag(ver: str) -> str: ...
def readthedocs_url(package_name: str, ver_: str = "latest") -> str: ...
def get_version(
    ver: str,
    is_use_final: bool = False,
) -> tuple[tuple[int, int, int, str, int], int]: ...
