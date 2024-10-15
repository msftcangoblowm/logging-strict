# once strictyaml implements type hints #90, this stub breaks
from strictyaml import (
    YAML,
    Enum,
    Validator,
)

__all__ = (
    "schema_logging_config",
    "validate_yaml_dirty",
)

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
    schema: Validator | None = ...,
) -> YAML | None: ...
