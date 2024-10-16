"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

Seperate constants out so independent of any dependencies

**Module private variables**

.. py:data:: _map_release
   :type: types.MappingProxyType
   :value: types.MappingProxyType({"alpha": "a", "beta": "b", "candidate": "rc"})

   Mapping of release levels. So can gracefully go back and forth

.. py:data:: __all__
   :type: tuple[str, str, str, str, str, str, str, str]
   :value: ("g_app_name", "__version_app", "LoggingConfigCategory", \
   "PREFIX_DEFAULT", "LOG_FORMAT", "FALLBACK_LEVEL", "sanitize_tag", \
   "get_version")

   Module exports

**Module objects**

.. py:data:: g_app_name
   :type: str
   :value: "logging_strict"

   App name. No hyphens. Lowercase. Not project name which can contain
   hyphen

.. py:data:: PREFIX_DEFAULT
   :type: str
   :value: "test_"

   unittest module default file name prefix

.. py:data:: LOG_FORMAT
   :type: str
   :value: "%(levelname)s %(module)s %(funcName)s: %(lineno)d: %(message)s"

   :py:mod:`logging` handlers contain formatters, which require a format
   str. Especially pertinent to unittests

.. py:data:: FALLBACK_LEVEL
   :type: str
   :value: "DEBUG"

   Fallback logging level, if provided level is an unsupported type, None, or empty str.
   So by default, this logging level, captures all.

.. py:data:: LOG_FMT_DETAILED
   :type: str
   :value: "%(asctime)s %(name)-15s %(levelname)-8s %(processName)-10s %(message)s"

   Detailed log message format. Notably includes: time, logger
   (worker) name, and process name

.. py:data:: LOG_FMT_SIMPLE
   :type: str
   :value: "%(name)-15s %(levelname)-8s %(processName)-10s %(message)s"

   Terse log message format. Notably includes: logger (worker) name and process name

.. py:data:: LOG_LEVEL_WORKER
   :type: str
   :value: "INFO"

   Show messages from :py:data:`logging.INFO` and higher

   .. seealso::

      - :py:meth:`coverage.control.Coverage.start`

      - :py:mod:`coverage.multiproc`


.. py:data:: version_info
   :type: tuple[int, int, int, str, int]

   Same semantics as :py:data:`sys.version_info`

.. py:data:: _dev
   :type: int

   .devN suffix, if any

.. py:data:: __version__
   :type: str

   Semantic versioning.

   :py:mod:`setuptools_scm` semantic versioning in: logging_strict._version.__version__

   .. code-block:: shell

      python igor.py bump_version

   ``igor.py`` updates this file, writing both version_info and _dev

   Dynamically generated by :py:mod:`setuptools_scm`
   if no patch or no tags at all SemVer will break.

   e.g. 2.1.devX instead of 2.0.1.devX

   Always include patch and ensure at least one tagged version

   .. seealso::

      :py:mod:`setuptools_scm`


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

g_app_name = "logging_strict"

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


LOG_FORMAT = "%(levelname)s %(module)s %(funcName)s: %(lineno)d: %(message)s"
FALLBACK_LEVEL = logging.getLevelName(logging.DEBUG)

# Thread pool worker
LOG_FMT_DETAILED = (
    "%(asctime)s %(name)-15s %(levelname)-8s %(processName)-10s %(message)s"
)
LOG_FMT_SIMPLE = "%(name)-15s %(levelname)-8s %(processName)-10s %(message)s"
LOG_LEVEL_WORKER = "INFO"

# Removes epoch and local. Fixes version
__version_app = sanitize_tag(__version__)
__url__ = readthedocs_url(g_app_name, ver_=__version__)
