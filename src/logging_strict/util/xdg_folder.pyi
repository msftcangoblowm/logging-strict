from pathlib import Path

__all__ = ("DestFolderSite", "DestFolderUser", "_get_path_config")

def _get_author(
    package: str,
    no_period: bool | None = True,
    no_space: bool | None = True,
    no_underscore: bool | None = True,
) -> str: ...

class DestFolderSite:
    def __init__(
        self,
        appname: str,
        author_no_period: bool | None = True,
        author_no_space: bool | None = True,
        author_no_underscore: bool | None = True,
        version: str | None = None,
        multipath: bool | None = False,
    ) -> None: ...
    @property
    def data_dir(self) -> str: ...
    @property
    def config_dir(self) -> str: ...

class DestFolderUser:
    def __init__(
        self,
        appname: str,
        author_no_period: bool | None = True,
        author_no_space: bool | None = True,
        author_no_underscore: bool | None = True,
        version: str | None = None,
        roaming: bool | None = False,
        opinion: bool | None = True,
    ) -> None: ...
    @property
    def data_dir(self) -> str: ...
    @property
    def config_dir(self) -> str: ...
    @property
    def cache_dir(self) -> str: ...
    @property
    def state_dir(self) -> str: ...
    @property
    def log_dir(self) -> str: ...

def _get_path_config(
    package: str,
    author_no_period: bool | None = True,
    author_no_space: bool | None = True,
    author_no_underscore: bool | None = True,
    version: str | None = None,
    roaming: bool | None = False,
) -> Path: ...
