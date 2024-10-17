"""
UI
---

:ref:`getting_started/usage:app`

Within UI process, call both:

- LoggingState

- ui_yaml_curated or setup_ui_other

worker process
---------------

:ref:`getting_started/usage:worker`

Step 1
~~~~~~~

Within worker entrypoint call either:

- worker_yaml_curated or setup_worker_other

Then pass str_yaml to the worker process

Step 2
~~~~~~~

Within worker process call

- setup_logging_yaml

Constants
----------

- LoggingConfigCategory
  :ref:`[constant docs] <code/constants/constants_general:top>`

tl;dr; ^^ won't need this ^^

Process categories Enum. Iterate over the Enum values, using class
method, `categories`.

`strict_logging` public methods are convenience functions for class,
`strict_logging.logging_api.LoggingConfigYaml`. If LoggingConfigYaml
used directly, choose one of the LoggingConfigCategory values to
pass as param, category.

Values: LoggingConfigCategory.UI or LoggingConfigCategory.WORKER

Corresponds to 'app' and 'worker'

Types
------

- LoggingYamlType
  :ref:`[type docs] <code/yaml/logging_yaml_abc:top>`

tl;dr; ^^ won't need this ^^

Useful only during strict type checking. class LoggingConfigYaml
implements LoggingYamlType interface and is a direct subclass

e.g. ``type[LoggingYamlType]``

Exceptions
-----------

:ref:`[exc docs] <code/constants/exceptions:exceptions>`

- LoggingStrictError

logging_strict catch all Exception. Base type of other exceptions.
Implements ValueError

Provided just for completeness. Not intended for use

- LoggingStrictPackageNameRequired

:abbr:`ep (entrypoint)` requires package name

Corresponding exit code -- 6

- LoggingStrictPackageStartFolderNameRequired

:abbr:`ep (entrypoint)` requires package start folder name

In logging-strict this is ``configs``. Normally its ``data``. But it can be anything

Corresponding exit code -- 7

- LoggingStrictProcessCategoryRequired

Applicable only during extract or setup, not during validation

Category required. Either:

LoggingConfigCategory.UI.value or LoggingConfigCategory.WORKER.value

Which corresponds to "app" or "worker"

- LoggingStrictGenreRequired

Applicable only during extract or setup, not during validation

UI framework terse name or worker implementation characteristic

e.g. textual, rich, :abbr:`mp (multiprocessing)` or :abbr:`mq (rabbitmq)`

"""

from .constants import LoggingConfigCategory
from .exceptions import (
    LoggingStrictError,
    LoggingStrictGenreRequired,
    LoggingStrictPackageNameRequired,
    LoggingStrictPackageStartFolderNameRequired,
    LoggingStrictProcessCategoryRequired,
)
from .logging_api import (
    LoggingState,
    setup_ui_other,
    setup_worker_other,
    ui_yaml_curated,
    worker_yaml_curated,
)
from .logging_yaml_abc import (
    LoggingYamlType,
    setup_logging_yaml,
)

__all__ = (
    "LoggingConfigCategory",
    "LoggingState",
    "LoggingYamlType",
    "setup_ui_other",
    "ui_yaml_curated",
    "setup_worker_other",
    "worker_yaml_curated",
    "setup_logging_yaml",
    "LoggingStrictError",
    "LoggingStrictPackageNameRequired",
    "LoggingStrictPackageStartFolderNameRequired",
    "LoggingStrictProcessCategoryRequired",
    "LoggingStrictGenreRequired",
)
