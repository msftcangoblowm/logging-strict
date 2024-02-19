import sys
from pathlib import Path
from typing import (
    Any,
    Optional,
)

if sys.version_info >= (3, 8):
    from typing import Final
else:
    from typing_extensions import Final

__all__: Final[tuple[str, str, str, str]]

def check_type_path(
    module_path: Optional[Any], *, msg_context: Optional[str] = None
) -> Path: ...
def is_not_ok(test: Optional[Any]) -> bool: ...
def is_ok(test: Optional[Any]) -> bool: ...
def check_int_verbosity(test: Optional[Any]) -> bool: ...
def check_start_folder_importable(folder_start: Optional[Any]) -> bool: ...
