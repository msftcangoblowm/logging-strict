"""
.. module:: logging_strict.exceptions
   :platform: Unix
   :synopsis: Custom exceptions

.. moduleauthor:: Dave Faulkmore <faulkmore telegram>

..

Custom exceptions

Public API
-----------

Usage

.. code-block:: python

    from logging_strict import (
        LoggingStrictError,
        LoggingStrictPackageNameRequired,
        LoggingStrictPackageStartFolderNameRequired,
        LoggingStrictProcessCategoryRequired,
        LoggingStrictGenreRequired,
    )

Module private variables
-------------------------

.. py:data:: __all__
   :type: tuple[str, str]
   :value: ("LoggingStrictError", "LoggingStrictPackageNameRequired", \
   "LoggingStrictPackageStartFolderNameRequired", \
   "LoggingStrictProcessCategoryRequired", "LoggingStrictGenreRequired")

   Module exports

Module objects
---------------

"""
__all__ = (
    "LoggingStrictError",
    "LoggingStrictPackageNameRequired",
    "LoggingStrictPackageStartFolderNameRequired",
    "LoggingStrictProcessCategoryRequired",
    "LoggingStrictGenreRequired",
)


class LoggingStrictError(ValueError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class LoggingStrictPackageNameRequired(LoggingStrictError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class LoggingStrictPackageStartFolderNameRequired(LoggingStrictError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class LoggingStrictProcessCategoryRequired(LoggingStrictError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class LoggingStrictGenreRequired(LoggingStrictError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)
