"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

Custom exceptions

Usage

.. code-block:: python

    from logging_strict import (
        LoggingStrictError,
        LoggingStrictPackageNameRequired,
        LoggingStrictPackageStartFolderNameRequired,
        LoggingStrictProcessCategoryRequired,
        LoggingStrictGenreRequired,
    )

**Module private variables**

.. py:data:: __all__
   :type: tuple[str, str, str, str, str]
   :value: ("LoggingStrictError", "LoggingStrictPackageNameRequired", \
   "LoggingStrictPackageStartFolderNameRequired", \
   "LoggingStrictProcessCategoryRequired", "LoggingStrictGenreRequired")

   Module exports

**Module objects**

"""

try:
    from importlib_metadata import PackageNotFoundError
except ImportError:  # pragma: no cover
    # What CPython provides likely very dated
    from importlib.metadata import PackageNotFoundError

__all__ = (
    "LoggingStrictError",
    "LoggingStrictPackageNameRequired",
    "LoggingStrictPackageStartFolderNameRequired",
    "LoggingStrictProcessCategoryRequired",
    "LoggingStrictGenreRequired",
    "PackageNotFoundError",
)


class LoggingStrictError(ValueError):
    """Catchall back exception

    :ivar msg: The error message
    :vartype msg: str
    """

    def __init__(self, msg):
        """Exception class constructor"""
        super().__init__(msg)


class LoggingStrictPackageNameRequired(LoggingStrictError):
    """In entrypoint, package name is required

    :ivar msg: The error message
    :vartype msg: str
    """

    def __init__(self, msg):
        """Exception class constructor"""
        super().__init__(msg)


class LoggingStrictPackageStartFolderNameRequired(LoggingStrictError):
    """In entrypoint, package start data folder name is required

    :ivar msg: The error message
    :vartype msg: str
    """

    def __init__(self, msg):
        """Exception class constructor"""
        super().__init__(msg)


class LoggingStrictProcessCategoryRequired(LoggingStrictError):
    """Category is required

    :ivar msg: The error message
    :vartype msg: str
    """

    def __init__(self, msg):
        """Exception class constructor"""
        super().__init__(msg)


class LoggingStrictGenreRequired(LoggingStrictError):
    """Genre is required

    :ivar msg: The error message
    :vartype msg: str
    """

    def __init__(self, msg):
        """Exception class constructor"""
        super().__init__(msg)
