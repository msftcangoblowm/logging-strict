from pathlib import Path
from typing import Any

__all__ = ("DestFolderSite", "DestFolderUser", "_get_path_config")

def _author_normalize(
    author_name: str,
    no_period: bool = True,
    no_space: bool = True,
    no_underscore: bool = True,
) -> str: ...
def _get_author(
    package: str,
    no_period: bool = True,
    no_space: bool = True,
    no_underscore: bool = True,
) -> str | None: ...

class XDGBase:
    appname: str
    _version: str | None
    _appauthor: str | None
    _no_period: bool
    _no_space: bool
    _no_underscore: bool

    __slots__ = (
        "_appauthor",
        "_no_period",
        "_no_space",
        "_no_underscore",
        "_version",
        "appname",
    )

    def __init__(
        self,
        appname: str,
        version: str | None = None,
        no_period: bool | None = True,
        no_space: bool | None = True,
        no_underscore: bool | None = True,
    ) -> None: ...
    @property
    def version(self) -> str | None: ...
    @version.setter
    def version(self, val: Any) -> None: ...
    @property
    def no_period(self) -> bool: ...
    @no_period.setter
    def no_period(self, val: Any) -> None: ...
    @property
    def no_space(self) -> bool: ...
    @no_space.setter
    def no_space(self, val: Any) -> None: ...
    @property
    def no_underscore(self) -> bool: ...
    @no_underscore.setter
    def no_underscore(self, val: Any) -> None: ...
    @property
    def appauthor(self) -> str | None: ...
    @appauthor.setter
    def appauthor(self, val: Any) -> None: ...

class DestFolderSite(XDGBase):
    _multipath: bool
    __slots__ = ("_multipath",)

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
    def multipath(self) -> bool: ...
    @multipath.setter
    def multipath(self, val: Any) -> None: ...
    @property
    def data_dir(self) -> str: ...
    @property
    def config_dir(self) -> str: ...

class DestFolderUser(XDGBase):
    _roaming: bool
    _opinion: bool
    __slots__ = ("_opinion", "_roaming")

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
    def opinion(self) -> bool: ...
    @opinion.setter
    def opinion(self, val: Any) -> None: ...
    @property
    def roaming(self) -> bool: ...
    @roaming.setter
    def roaming(self, val: Any) -> None: ...
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
