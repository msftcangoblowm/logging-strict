import logging
from collections.abc import Sequence
from typing import TextIO

__all__ = ("LoggerRedirector",)

# non-async unittest streams redirector

class LoggerRedirector:
    _real_stdout: TextIO
    _real_stderr: TextIO

    @staticmethod
    def all_loggers() -> Sequence[logging.Logger]: ...
    @classmethod
    def redirect_loggers(
        cls,
        fake_stdout: TextIO | None = None,
        fake_stderr: TextIO | None = None,
    ) -> None: ...
    @classmethod
    def reset_loggers(
        cls,
        fake_stdout: TextIO | None = None,
        fake_stderr: TextIO | None = None,
    ) -> None: ...
