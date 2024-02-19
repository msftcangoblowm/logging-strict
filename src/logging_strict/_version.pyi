from __future__ import annotations

import sys

if sys.version_info >= (3, 8):
    from typing import Final
else:
    from typing_extensions import Final

version: Final[str]
__version__: Final[str]
__version_tuple__: Final[tuple[int | str, ...]]
version_tuple: Final[tuple[int | str, ...]]
