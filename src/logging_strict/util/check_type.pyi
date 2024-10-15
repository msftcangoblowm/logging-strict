from pathlib import Path
from typing import Any

__all__ = (
    "check_type_path",
    "is_not_ok",
    "is_ok",
    "check_int_verbosity",
    "check_start_folder_importable",
)

def check_type_path(
    module_path: Any | None,
    *,
    msg_context: str | None = None,
) -> Path: ...
def is_not_ok(test: Any | None) -> bool: ...
def is_ok(test: Any | None) -> bool: ...
def check_int_verbosity(test: Any | None) -> bool: ...
def check_start_folder_importable(folder_start: Any | None) -> bool: ...
