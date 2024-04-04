# once strictyaml implements type hints #90, this stub breaks
from __future__ import annotations

import sys

from strictyaml import (
    YAML,
    Enum,
    Validator,
)
from strictyaml.validators import Validator

if sys.version_info >= (3, 8):
    from typing import Final
else:
    from typing_extensions import Final

__all__: Final[tuple[str, str]]

format_style: Enum
format_style_default: str
levels: Enum
logger_keys: Enum
logging_config_keys: Enum

formatter_map: Validator
filters_map: Validator
handlers_map: Validator
loggers_map: Validator
root_map: Validator

schema_logging_config: Validator

def validate_yaml_dirty(
    yaml_snippet: str,
    schema: Validator | None = schema_logging_config,
) -> YAML | None: ...
