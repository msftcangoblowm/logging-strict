import sys

if sys.version_info >= (3, 8):
    from typing import Final
else:
    from typing_extensions import Final

__all__: Final[tuple[str, str, str, str, str]]

class LoggingStrictError(ValueError):
    def __init__(self, msg: str) -> None: ...

class LoggingStrictPackageNameRequired(LoggingStrictError):
    def __init__(self, msg: str) -> None: ...

class LoggingStrictPackageStartFolderNameRequired(LoggingStrictError):
    def __init__(self, msg: str) -> None: ...

class LoggingStrictProcessCategoryRequired(LoggingStrictError):
    def __init__(self, msg: str) -> None: ...

class LoggingStrictGenreRequired(LoggingStrictError):
    def __init__(self, msg: str) -> None: ...
