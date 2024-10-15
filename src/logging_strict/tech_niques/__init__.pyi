import enum
from typing import Any

from .context_locals import get_locals
from .coverage_misbehaves import detect_coverage
from .logger_redirect import LoggerRedirector
from .logging_capture import captureLogs
from .stream_capture import CaptureOutput

__all__ = (
    "get_locals",
    "is_class_attrib_kind",
    "ClassAttribTypes",
    "LoggerRedirector",
    "captureLogs",
    "detect_coverage",
    "CaptureOutput",
)

class ClassAttribTypes(enum.Enum):
    CLASSMETHOD = "class method"
    STATICMETHOD = "static method"
    PROPERTY = "property"
    METHOD = "method"
    DATA = "data"

def is_class_attrib_kind(
    cls: type[Any], str_m: Any, kind: ClassAttribTypes
) -> bool: ...
