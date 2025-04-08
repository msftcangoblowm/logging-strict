import sys
from collections.abc import Callable
from types import (
    BuiltinFunctionType,
    BuiltinMethodType,
    ClassMethodDescriptorType,
    FunctionType,
    MethodDescriptorType,
    MethodType,
    MethodWrapperType,
    ModuleType,
    WrapperDescriptorType,
)
from typing import (
    Any,
    Protocol,
    TypeVar,
)
from unittest.mock import MagicMock

if sys.version_info >= (3, 10):  # pragma: no cover
    from typing import (
        ParamSpec,
        TypeAlias,
    )
else:  # pragma: no cover
    from typing_extensions import (
        ParamSpec,
        TypeAlias,
    )

_T = TypeVar("_T")  # Can be anything
_P = ParamSpec("_P")
_R: TypeAlias = tuple[_T, dict[str, Any]]

__all__ = (
    "FuncWrapper",
    "get_locals",
    "get_locals_dynamic",
)

class FuncWrapper:
    def __init__(
        self,
        func: (
            FunctionType
            | MethodType
            | BuiltinFunctionType
            | BuiltinMethodType
            | WrapperDescriptorType
            | MethodWrapperType
            | MethodDescriptorType
            | ClassMethodDescriptorType
        ),
    ) -> None: ...
    @staticmethod
    def _get_method_parent(meth: Any) -> type | None: ...
    @property
    def name(self) -> str: ...
    @property
    def cls(self) -> type | None: ...
    @property
    def cls_name(self) -> str | None: ...
    @property
    def module(self) -> ModuleType | None: ...
    @property
    def module_name(self) -> str | None: ...
    @property
    def module_filename(self) -> str | None: ...
    @property
    def package_name(self) -> str: ...
    @property
    def root_package_name(self) -> str: ...
    @property
    def full_name(self) -> str: ...
    def get_dotted_path(self) -> str: ...

def _func(param_a: str, param_b: int | None = 10) -> str: ...

class MockFunction(Protocol[_P, _R[_T]]):  # type: ignore[misc]
    def __init__(self, func: Callable[_P, _T]) -> None: ...
    def __call__(  # type: ignore[misc]  # missing self non-static method
        mock_instance: MagicMock,
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> _R[_T]: ...

class MockMethod(Protocol[_P, _R[_T]]):  # type: ignore[misc]
    def __init__(self, cls: type, func: Callable[_P, _T]) -> None: ...
    def __call__(  # type: ignore[misc]  # missing self non-static method
        mock_instance: MagicMock,
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> _R[_T]: ...

def get_locals_dynamic(
    func: Callable[_P, _T],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> _R[_T]: ...
def get_locals(
    func_path: str,
    func: Callable[_P, _T],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> _R[_T]: ...
