import sys
from typing import (
    Any,
    Callable,
    TypeVar,
)
from unittest.mock import MagicMock

if sys.version_info >= (3, 8):  # pragma: no cover
    from typing import Final
else:  # pragma: no cover
    from typing_extensions import Final

if sys.version_info >= (3, 10):  # pragma: no cover
    from collections.abc import Callable
    from typing import ParamSpec
else:  # pragma: no cover
    from typing import Callable

    from typing_extensions import ParamSpec

T = TypeVar("T")  # Can be anything
P = ParamSpec("P")

__all__: Final[tuple[str]]

class MockFunction:
    def __init__(self, func: Callable[..., Any]) -> None: ...
    def __call__(  # type: ignore[misc]  # missing self non-static method
        mock_instance: MagicMock,
        /,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Any: ...

def get_locals(
    func_path: str,
    func: Callable[..., Any],
    /,
    *args: P.args,
    **kwargs: P.kwargs,
) -> tuple[T, dict[str, Any]]: ...
