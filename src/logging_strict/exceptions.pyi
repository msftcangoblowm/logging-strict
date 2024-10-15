__all__ = (
    "LoggingStrictError",
    "LoggingStrictPackageNameRequired",
    "LoggingStrictPackageStartFolderNameRequired",
    "LoggingStrictProcessCategoryRequired",
    "LoggingStrictGenreRequired",
)

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
