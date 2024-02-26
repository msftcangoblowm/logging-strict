import enum
import sys
from typing import Any

if sys.version_info >= (3, 8):
    from typing import Final
else:
    from typing_extensions import Final

__all__: Final[tuple[str, str, str, str, str, str, str]]

class ClassAttribTypes(enum.Enum):
    CLASSMETHOD = "class method"
    STATICMETHOD = "static method"
    PROPERTY = "property"
    METHOD = "method"
    DATA = "data"

def is_class_attrib_kind(
    cls: type[Any], str_m: Any, kind: ClassAttribTypes
) -> bool: ...
