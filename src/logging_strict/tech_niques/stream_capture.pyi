import sys
from types import TracebackType
from typing import (
    Any,
    Optional,
)

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
        exc_type: Optional[type[Exception]],
        exc_value: Optional[Any],
        exc_tb: Optional[TracebackType],
    ) -> None: ...
    @property
    def stdout(self) -> str: ...
    @property
    def stderr(self) -> str: ...
