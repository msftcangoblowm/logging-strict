from __future__ import annotations

import logging
import sys
from typing import TextIO

if sys.version_info >= (3, 8):
    from typing import Final
else:
    from typing_extensions import Final

if sys.version_info >= (3, 9):
    from collections.abc import Sequence
else:
    from typing import Sequence

__all__: Final[tuple[str]]

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
