import sys
from pathlib import Path
from typing import Optional

if sys.version_info >= (3, 8):  # pragma: no cover
    from typing import Final
else:  # pragma: no cover
    from typing_extensions import Final

__all__: Final[tuple[str, str, str]]

def _get_author(
    package: str,
    no_period: Optional[bool] = True,
    no_space: Optional[bool] = True,
    no_underscore: Optional[bool] = True,
) -> str: ...

class DestFolderSite:
    def __init__(
        self,
        appname: str,
        author_no_period: Optional[bool] = True,
        author_no_space: Optional[bool] = True,
        author_no_underscore: Optional[bool] = True,
        version: Optional[str] = None,
        multipath: Optional[bool] = False,
    ) -> None: ...
    @property
    def data_dir(self) -> str: ...
    @property
    def config_dir(self) -> str: ...

class DestFolderUser:
    def __init__(
        self,
        appname: str,
        author_no_period: Optional[bool] = True,
        author_no_space: Optional[bool] = True,
        author_no_underscore: Optional[bool] = True,
        version: Optional[str] = None,
        roaming: Optional[bool] = False,
        opinion: Optional[bool] = True,
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
    author_no_period: Optional[bool] = True,
    author_no_space: Optional[bool] = True,
    author_no_underscore: Optional[bool] = True,
    version: Optional[str] = None,
    roaming: Optional[bool] = False,
) -> Path: ...
