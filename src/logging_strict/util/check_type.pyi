from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 8):
    from typing import Final
else:
    from typing_extensions import Final

__all__: Final[tuple[str, str, str, str, str]]

def check_type_path(
    module_path: Any | None,
    *,
    msg_context: str | None = None,
) -> Path: ...
def is_not_ok(test: Any | None) -> bool: ...
def is_ok(test: Any | None) -> bool: ...
def check_int_verbosity(test: Any | None) -> bool: ...
def check_start_folder_importable(folder_start: Any | None) -> bool: ...
