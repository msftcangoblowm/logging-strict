"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

Seperate constants out reduce any dependencies imports.

"""

from __future__ import annotations

import logging  # noqa: F401 used by sphinx
from enum import Enum
from typing import Any  # noqa: F401 used by sphinx

from ._version import __version__
from .version_semantic import (
    readthedocs_url,
    sanitize_tag,
)

__all__ = (
    "g_app_name",
    "__version_app",
    "__url__",
    "PREFIX_DEFAULT",
    "LoggingConfigCategory",
    "LOG_FORMAT",
    "FALLBACK_LEVEL",
)

#: str: App name. No hyphens. Lowercase
g_app_name = "logging_strict"

#: str: unittest module default file name prefix
PREFIX_DEFAULT = "test_"


def enum_map_func_get_value(enum_item):
    """func for use with Python built-in :py:func:`map`, to get the
    value of an Enum item

    :param enum_item: Enum subclass item. Get the Enum item value
    :type enum_item: type[enum.Enum]
    :returns: Enum item value. Can be anything but usually a str or int
    :rtype: typing.Any
    """
    return enum_item.value


class LoggingConfigCategory(Enum):
    """logging.config yaml process categories

    Public API

    .. code-block:: text

       from logging_strict import LoggingConfigCategory

    """

    WORKER = "worker"
    UI = "app"

    @classmethod
    def categories(cls):
        """Get Enum items' value

        :returns: In this case, Enum values holds str
        :rtype: collections.abc.Iterator[str]
        """
        values = cls._member_map_.values()
        yield from map(enum_map_func_get_value, values)


#: str: logging handlers contain formatters, which require a format str
LOG_FORMAT = "%(levelname)s %(module)s %(funcName)s: %(lineno)d: %(message)s"

#: str: Fallback logging level, if provided level is an unsupported type, None, or empty str
FALLBACK_LEVEL = logging.getLevelName(logging.DEBUG)

#: str: Detailed log message format for Thread pool worker.
LOG_FMT_DETAILED = (
    "%(asctime)s %(name)-15s %(levelname)-8s %(processName)-10s %(message)s"
)

#: str: Terse log message format. Notably includes: logger (worker) name and process name
LOG_FMT_SIMPLE = "%(name)-15s %(levelname)-8s %(processName)-10s %(message)s"

#: str: Show messages from logging.INFO and higher
LOG_LEVEL_WORKER = "INFO"

#: str: Removes epoch and local. Fixes version
__version_app = sanitize_tag(__version__)

#: str: URL to RTD manual
__url__ = readthedocs_url(g_app_name, ver_=__version__)
