import sys
from types import TracebackType
from typing import TextIO

from typing_extensions import Self

__all__ = ("CaptureOutput",)

class CaptureOutput:
    __slots__ = ("_stdout_output", "_stderr_output", "_stdout", "_stderr")
    _stdout: TextIO
    _stderr: TextIO
    _stdout_output: str
    _stderr_output: str

    def __enter__(self) -> Self: ...
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None: ...
    @property
    def stdout(self) -> str: ...
    @property
    def stderr(self) -> str: ...
