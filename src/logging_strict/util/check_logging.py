"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

..

Checks dealing with logging module

**Module private variables**

.. py:data:: __all__
   :type: tuple[str, str, str, str, str, str]
   :value: ("is_assume_root", "check_logger", "check_level_name", \
   "check_level", "check_formatter", "str2int")

   Exported objects from this module

**Module objects**

"""

from __future__ import annotations

import logging
import sys

from ..constants import LOG_FORMAT
from .check_type import (
    is_not_ok,
    is_ok,
)

__all__ = (
    "is_assume_root",
    "check_logger",
    "check_level_name",
    "check_level",
    "check_formatter",
    "str2int",
)

# ####################
# MONKEYPATCH logging module -- backporting py311 feature
# ####################

if sys.version_info < (3, 11):  # pragma: no cover

    def getLevelNamesMapping() -> dict[str, int]:
        """Backport of py311 feature getLevelNamesMapping

        :returns: Copy of mapping level names to level int values
        :rtype: dict[str, int]
        """
        return logging._nameToLevel.copy()

    logging.getLevelNamesMapping = getLevelNamesMapping
else:  # pragma: no cover
    pass


def str2int(level=None):
    """Support both integer levels as int or as a str. Try to convert.
    If possible to convert str -> int. Otherwise ``False``

    :param level: Can be
    :type level: typing.Any | None
    :returns: ``False`` if cannot convert str -> int otherwise the int
    :rtype: int | bool
    """
    try:
        int_ret = int(level)
    except Exception:
        ret = False
    else:  # pragma: no cover
        ret = int_ret if is_ok(level) else False

    return ret


def is_assume_root(logger_name):
    """Consider all these to be root:

    - None
    - Empty string
    - String containing only whitespace
    - "root"

    :param logger_name: A logger name
    :type logger_name: typing.Any | None
    :returns: True if should assume is root loger name otherwise False
    :rtype: bool
    """
    ret = (
        logger_name is None
        or (
            logger_name is not None
            and isinstance(logger_name, str)
            and is_not_ok(logger_name)
        )
        or (
            logger_name is not None
            and isinstance(logger_name, str)
            and logger_name == "root"
        )
    )

    return ret


def check_logger(logger):
    """Check working with a :py:class:`logging.Logger`

    :param logger:

       Logger name can be a :py:class:`logging.Logger` or str

    :type logger: typing.Any | str | ``None``
    :returns: Would produce a normalized logger
    :rtype: bool
    """
    _logger_name = logger
    if is_assume_root(_logger_name):
        # Assume root as the logging module does
        ret = True
    else:
        if isinstance(_logger_name, logging.Logger):
            ret = True
        elif is_ok(_logger_name):
            ret = True
        else:
            ret = False

    return ret


def check_level_name(logger_name):
    """Check logger level name

    :param logger_name:

       Logger name can be a :py:class:`logging.Logger`, str

    :type logger_name: typing.Any | ``None``
    :returns: ``True`` check pass otherwise ``False``
    :rtype: bool
    """
    if is_assume_root(logger_name):
        # None or empty string (after strip)
        # root logger
        ret = True
    else:
        if isinstance(logger_name, logging.Logger):
            ret = True
        elif isinstance(logger_name, str):
            # Will accept any non-empty crazy str, e.g. ``"s,a*d&f#as%df"``
            ret = True
        else:
            ret = False

    return ret


def check_level(level):
    """Check whether or not
    :paramref:`~logging_strict.util.check_logging.check_level.params.level`
    can be normalized into a logging level name

    :param level:

       str or int or :py:data:`logging.INFO` (, etc) or :py:data:`~typing.Any`

    :type level: typing.Any | None
    :returns: ``True`` level can be normalized otherwise ``False``
    :rtype: bool
    """
    if is_assume_root(level):
        """Guess referring to root logger. Avoid making a disasterous
        assumption with horrible side effects"""
        ret = True
    else:
        if isinstance(level, logging.Logger):
            ret = True
        elif isinstance(level, str):
            if level in logging.getLevelNamesMapping().keys():
                # "INFO"
                ret = True
            elif level in map(str, logging.getLevelNamesMapping().values()):
                """After mapping logging levels to str, compares str. No
                need for is_str_convertable"""
                ret = True
            else:
                is_str_convertable = str2int(level=level)
                if not isinstance(is_str_convertable, bool) and isinstance(
                    is_str_convertable, int
                ):
                    if is_str_convertable > 0 and is_str_convertable < 50:
                        # Although valid, KISS principle
                        ret = False
                    elif is_str_convertable < 0:
                        # outside of range
                        ret = False
                    elif is_str_convertable > 50:
                        # outside of range
                        ret = False
                    else:  # pragma: no cover
                        pass
                else:
                    # Not convertible into an int
                    ret = is_str_convertable
        elif isinstance(level, int):
            if level in logging.getLevelNamesMapping().values():
                # in predefined logging levels (e.g. 10)
                ret = True
            elif level not in logging.getLevelNamesMapping().values() and (
                (level > 0 and level < 50) or level < 0 or level > 50
            ):
                # Although valid, KISS principle
                # outside of range
                ret = False
            else:  # pragma: no cover All possible int covered
                ret = False
        else:
            ret = False

    return ret


def check_formatter(format_=LOG_FORMAT):
    """Check logging format str

    :param format_: Default ``LOG_FORMAT``

       Can pass in anything. Intended to be a logging format str

    :type format_: typing.Any | None
    :returns: ``True`` if a valid logging formatter str otherwise ``False``
    :rtype: bool
    """
    if format_ is None or is_not_ok(format_):
        # Invalid so would be assigned the default
        ret = False
    else:
        # TypeError impossible cuz restricted to non-empty str
        format_str = format_
        try:
            logging.Formatter(format_str)
        except ValueError:
            ret = False
        else:
            ret = True

    return ret
