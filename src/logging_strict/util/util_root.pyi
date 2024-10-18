import logging
from collections.abc import Callable
from pathlib import Path
from typing import (
    Any,
    Final,
)

__all__ = (
    "IsRoot",
    "check_python_not_old",
)

g_module: Final[str]
_LOGGER: Final[logging.Logger]
g_is_root: bool
is_python_old: Final[bool]

def is_user_admin() -> bool: ...
def get_logname() -> str: ...
def ungraceful_app_exit() -> None: ...

class IsRoot:
    __slots__ = ()

    @staticmethod
    def is_root() -> bool: ...
    @classmethod
    def path_home_root(cls) -> Path: ...
    @classmethod
    def check_root(
        cls,
        callback: Callable[[], str] | None = None,
        is_app_exit: bool | None = False,
        is_raise_exc: bool | None = False,
    ) -> None: ...
    @classmethod
    def check_not_root(
        cls,
        callback: Callable[[], str] | None = None,
        is_app_exit: bool | None = False,
        is_raise_exc: bool | None = False,
    ) -> None: ...
    @classmethod
    def set_owner_as_user(
        cls,
        path_file: Any,
        is_as_user: Any | None = False,
    ) -> None: ...

def check_python_not_old(
    callback: Callable[[], str] | None = None,
    is_app_exit: bool | None = False,
    is_raise_exc: bool | None = False,
) -> None: ...
