from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 8):
    from typing import Final
else:
    from typing_extensions import Final

if sys.version_info >= (3, 9):
    from collections.abc import Sequence
else:
    from typing import Sequence

__all__: Final[tuple[str, str]]

@lru_cache
def find_project_root(
    srcs: Sequence[Any] | None,
    stdin_filename: str | None = None,
) -> tuple[Path, str]: ...
def find_pyproject_toml(
    path_search_start: tuple[str, ...],
    stdin_filename: str | None = None,
) -> str | None: ...
