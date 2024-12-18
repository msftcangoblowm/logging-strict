import sys
from collections.abc import Callable
from typing import (
    Any,
    TypeVar,
)
from unittest.mock import MagicMock

if sys.version_info >= (3, 10):  # pragma: no cover
    from typing import ParamSpec
else:  # pragma: no cover
    from typing_extensions import ParamSpec

_T = TypeVar("_T")  # Can be anything
_P = ParamSpec("_P")

__all__ = ("get_locals",)

def _func(param_a: str, param_b: int | None = 10) -> str: ...

class MockFunction:
    def __init__(self, func: Callable[..., Any]) -> None: ...
    def __call__(  # type: ignore[misc]  # missing self non-static method
        mock_instance: MagicMock,
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> Any: ...

def get_locals(
    func_path: str,
    func: Callable[..., Any],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> tuple[_T, dict[str, Any]]: ...
