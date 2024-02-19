import sys
from pathlib import Path
from typing import (
    Any,
    ClassVar,
    Optional,
)

# py39
if sys.version_info >= (3, 9):
    from collections.abc import Callable
else:
    from typing import Callable

__all__: tuple[str, str]

g_is_root: bool
is_python_old: bool

def get_logname() -> str: ...
def ungraceful_app_exit() -> None: ...

class IsRoot:
    __slots__: ClassVar[tuple[()]]
    _is_root: ClassVar[bool]

    @staticmethod
    def is_root() -> bool: ...
    @classmethod
    def path_home_root(cls) -> Path: ...
    @classmethod
    def check_root(
        cls,
        callback: Optional[Callable[[], str]] = None,
        is_app_exit: Optional[bool] = False,
        is_raise_exc: Optional[bool] = False,
    ) -> None: ...
    @classmethod
    def check_not_root(
        cls,
        callback: Optional[Callable[[], str]] = None,
        is_app_exit: Optional[bool] = False,
        is_raise_exc: Optional[bool] = False,
    ) -> None: ...
    @classmethod
    def set_owner_as_user(
        cls,
        path_file: Any,
        is_as_user: Optional[Any] = False,
    ) -> None: ...

def check_python_not_old(
    callback: Optional[Callable[[], str]] = None,
    is_app_exit: Optional[bool] = False,
    is_raise_exc: Optional[bool] = False,
) -> None: ...
