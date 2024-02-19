__all__ = (
    "LoggingStrictError",
    "LoggingStrictPackageNameRequired",
    "LoggingStrictPackageStartFolderNameRequired",
    "LoggingStrictProcessCategoryRequired",
    "LoggingStrictGenreRequired",
)


class LoggingStrictError(ValueError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class LoggingStrictPackageNameRequired(LoggingStrictError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class LoggingStrictPackageStartFolderNameRequired(LoggingStrictError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class LoggingStrictProcessCategoryRequired(LoggingStrictError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class LoggingStrictGenreRequired(LoggingStrictError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)
