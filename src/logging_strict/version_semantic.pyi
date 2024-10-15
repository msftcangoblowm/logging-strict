import types

__all__ = (
    "sanitize_tag",
    "get_version",
    "readthedocs_url",
)

_map_release: types.MappingProxyType[str, str]

def sanitize_tag(ver: str) -> str: ...
def readthedocs_url(package_name: str, ver_: str = "latest") -> str: ...
def get_version(
    ver: str,
    is_use_final: bool = False,
) -> tuple[tuple[int, int, int, str, int], int]: ...
