from __future__ import annotations

import sys
from types import TracebackType
from typing import Any

if sys.version_info >= (3, 8):
    from typing import Final
else:
    from typing_extensions import Final

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

__all__: Final[tuple[str]]

class CaptureOutput:
    def __enter__(self) -> Self: ...
    def __exit__(
        self,
        exc_type: type[Exception] | None,
        exc_value: Any | None,
        exc_tb: TracebackType | None,
    ) -> None: ...
    @property
    def stdout(self) -> str: ...
    @property
    def stderr(self) -> str: ...
