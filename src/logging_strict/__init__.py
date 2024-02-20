"""
.. py:module:: logging_strict
   :platform: Unix
   :synopsis: Public interface

.. moduleauthor:: Dave Faulkmore <faulkmore telegram>

..

UI process call
-------------------

- LoggingState

- setup_ui

worker process -- step 1
-----------------------------------

Within worker entrypoint call either:

- worker_yaml_curated

or

- setup_worker_other

Then pass str_yaml to the worker process

Called by worker process -- step 2
-----------------------------------

Within worker process call

- setup_logging_yaml

Module private variables
-------------------------

.. py:data:: __all__
   :type: tuple[str, str, str, str, str, str, str, str, str, str, str, str]
   :value: ("LoggingConfigCategory", "LoggingState", "LoggingYamlType", "setup_ui", \
   "worker_yaml_curated", "setup_worker_other", "setup_logging_yaml", \
   "LoggingStrictError", "LoggingStrictPackageNameRequired", \
   "LoggingStrictPackageStartFolderNameRequired", \
   "LoggingStrictProcessCategoryRequired", "LoggingStrictGenreRequired")

   Module exports

Module objects
---------------

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
    setup_ui,
    setup_worker_other,
    worker_yaml_curated,
)
from .logging_yaml_abc import (
    LoggingYamlType,
    setup_logging_yaml,
)

__all__ = (
    LoggingConfigCategory,
    LoggingState,
    LoggingYamlType,
    setup_ui,
    setup_worker_other,
    worker_yaml_curated,
    setup_logging_yaml,
    LoggingStrictError,
    LoggingStrictPackageNameRequired,
    LoggingStrictPackageStartFolderNameRequired,
    LoggingStrictProcessCategoryRequired,
    LoggingStrictGenreRequired,
)
