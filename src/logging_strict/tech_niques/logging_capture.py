"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

..

Within a context manager, capture log messages from third party packages

Capture logging messages from package `foo`, INFO level and higher,
into a list.

Can optionally set formatting. Has sane default, normally leave out the
logging message format string.

.. testcode::

    import logging

    from logging_strict.tech_niques import captureLogs
    from logging_strict.constants import LOG_FORMAT

    msg0 = 'first msg'
    msg1 = 'second msg'

    with captureLogs('foo', level='INFO', format_=LOG_FORMAT) as cm:
        logging.getLogger('foo').info(msg0)
        logging.getLogger('foo.bar').error(msg1)

    out = cm.output
    line0 = out[0]
    line1 = out[1]
    assert "INFO" in line0
    assert msg0 in line0
    assert "ERROR" in line1
    assert msg1 in line1

Can be chained with other context managers. Such as capturing the streams as well

.. testcode::

    import logging
    import sys

    from logging_strict.tech_niques import CaptureOutput, captureLogs

    msg0 = 'first msg'
    msg1 = 'second msg'
    msg_err = "StdMoooooo!"
    msg_out = "StdMagpie"
    with (
        captureLogs('foo', level='INFO') as cm,
        CaptureOutput() as cow,
    ):
        logging.getLogger('foo').info(msg0)
        logging.getLogger('foo.bar').error(msg1)
        sys.stdout.write(msg_out)
        sys.stderr.write(msg_err)

    assert cow.stderr == msg_err
    assert cow.stdout == msg_out

    out = cm.output
    line0 = out[0]
    line1 = out[1]
    assert "INFO" in line0
    assert msg0 in line0
    assert "ERROR" in line1
    assert msg1 in line1

with block using parentheses style is useful when there is more than
one context manager. Even with only one context manager, with block
using parentheses is the preferred style.

When when chaining context managers together, it's a one liner

In addition to the two context managers above, in unittests,
:py:func:`unittest.mock.patch` can alter modules behavior
and results without changes to the modules source code.

sync and async logging
-----------------------

- For
  :ref:`synchronous logging <api/logging/api_logging_synchronous:synchronous logging>`,
  a context manager to fix the issue of redirecting stdout/stderr.

  :py:class:`LoggerRedirector <logging_strict.tech_niques.LoggerRedirector>`

  :code:`from logging_strict.tech_niques import LoggerRedirector`

- For asynchronous logging, using package,
  :ref:`aiologger <api/logging/api_logging_asynchronous:asynchronous logging>`

unittest assertLogs/assertNoLogs
---------------------------------

tl;dr;
^^^^^^^

:py:meth:`unittest.TestCase.assertLogs` assertion makes it
ill-suited for general use, besides within unittests

The details
^^^^^^^^^^^^

:py:meth:`unittest.TestCase.assertLogs` does log capturing

    **Tests** that **at least one message is logged** on the logger or
    one of its children, with at least the given level.

:menuselection:`captureLogs --> does no assertion`

:menuselection:`assertLogs --> does assertion`

So captureLogs is suitable for general usage

Having made that strong disclaimer, lets see how assertLogs works

Code snippet
^^^^^^^^^^^^^

- Source unittest docs

- Confirmed in unittest #12, tests/utils/test_logging_capture

.. code-block:: text

   class DocumentAssertLogs(unittest.TestCase):
       def test_assert_logging_output(self):
           with self.assertLogs('foo', level='INFO') as cm:
               logging.getLogger('foo').info('first message')
               logging.getLogger('foo.bar').error('second message')
           self.assertEqual(cm.output, [
               'INFO:foo:first message',
               'ERROR:foo.bar:second message',
           ])


.. seealso::

   assertLogs :py:meth:`[docs] <unittest.TestCase.assertLogs>`
   `[source] <https://github.com/python/cpython/blob/db6f297d448ce46e58a5b90239a4779553333198/Lib/unittest/case.py#L816>`_

   assertNoLogs (py310+) :py:meth:`[docs] <unittest.TestCase.assertNoLogs>`

Into the rabbit hole
---------------------------

More in-depth low level implementation notes

.. seealso::

   unittest._log

   - _CapturingHandler
   -  _AssertLogsContext

   https://github.com/python/cpython/blob/cd87737a1de9a3b766358912985ffae511c3911d/Lib/unittest/_log.py

   unittest.case.TestCase

   - _BaseTestCaseContext

   https://github.com/python/cpython/blob/db6f297d448ce46e58a5b90239a4779553333198/Lib/unittest/case.py#L193


**Module private variables**

.. py:data:: __all__
   :type: tuple[str, str]
   :value: ("captureLogs", "captureLogsMany")

   Exported objects from this module

**Module objects**

"""

from __future__ import annotations

import contextlib
import logging
import sys

import attrs

from ..constants import LOG_FORMAT
from ..util.check_logging import (
    check_formatter,
    check_level,
    is_assume_root,
    str2int,
)
from ..util.check_type import (
    is_not_ok,
    is_ok,
)

if sys.version_info >= (3, 8):  # pragma: no cover
    from collections.abc import (  # noqa: F401 Used by Sphinx
        MutableSequence,
        Sequence,
    )
else:  # pragma: no cover
    from typing import (  # noqa: F401 Used by Sphinx
        MutableSequence,
        Sequence,
    )

if sys.version_info >= (3, 9):  # pragma: no cover
    from collections.abc import Iterator  # noqa: F401 Used by sphinx
else:  # pragma: no cover
    from typing import Iterator  # noqa: F401 Used by sphinx

__all__ = ("captureLogs", "captureLogsMany")

# ####################
# MONKEYPATCH logging module -- backporting py312 features
# ####################

if sys.version_info < (3, 11):  # pragma: no cover py311 feature

    def getLevelNamesMapping() -> dict[str, int]:
        """Backport: getLevelNamesMapping

        :returns: mapping of logging level name to int value
        :rtype: dict[str, int]
        """
        return logging._nameToLevel.copy()

    logging.getLevelNamesMapping = getLevelNamesMapping
else:  # pragma: no cover
    # test_logging_capture imports getLevelNamesMapping
    getLevelNamesMapping = logging.getLevelNamesMapping

if sys.version_info < (3, 12):  # pragma: no cover py312 feature
    # Backport: logging.getHandlerByName and logging.getHandlerNames
    def getHandlerByName(name: str) -> type[logging.Handler]:
        """
        Get a handler with the specified *name*, or None if there isn't one with
        that name.
        """
        return logging._handlers.get(name)

    logging.getHandlerByName = getHandlerByName

    def getHandlerNames() -> frozenset[str]:
        """
        Return all known handler names as an immutable set.
        """
        result = set(logging._handlers.keys())
        return frozenset(result)

    logging.getHandlerNames = getHandlerNames

    def getChildren(self) -> set[logging.Logger]:
        """Logger.getChildren method added in py312. Hopefully helpful
        in diagnosing issues affecting loggers and their handlers
        """

        def _hierlevel(logger):
            """From logger root child hierarchy level

            :param logger: logger instance. Counts periods plus 1
            :type logger: logging.Logger
            :returns: loggers hierarchy level
            :rtype: int
            """
            if logger is logger.manager.root:
                return 0
            return 1 + logger.name.count(".")

        d = self.manager.loggerDict
        logging._acquireLock()
        try:
            # exclude PlaceHolders - the last check is to ensure that lower-level
            # descendants aren't returned - if there are placeholders, a logger's
            # parent field might point to a grandparent or ancestor thereof.
            return set(
                item
                for item in d.values()
                if isinstance(item, logging.Logger)
                and item.parent is self
                and _hierlevel(item) == 1 + _hierlevel(item.parent)
            )
        finally:
            logging._releaseLock()

    logging.Logger.getChildren = getChildren

else:  # pragma: no cover
    getHandlerByName = logging.getHandlerByName
    getHandlerNames = logging.getHandlerNames
    getChildren = logging.Logger.getChildren


def _normalize_level(level):
    """For
    :py:func:`logging_strict.tech_niques.logging_capture.captureLogs`,
    normalize level

    :param level:

       str or int or :py:data:`logging.INFO` (, etc) or :py:data:`~typing.Any`

    :type level: typing.Any | None
    :returns: Normalized logger level name
    :rtype: str
    :raise:

       - :py:exc:`ValueError` -- Invalid int logging level
       - :py:exc:`TypeError` -- Unsupported type. Not a logging level

    """
    msg_typerror = f"Unsupported type, {type(level)}"
    msg_valueerror_int = (
        f"Invalid logging level {str(level)} or out of range. "
        "Keep within KISS principle"
    )
    msg_valueerror_str = (
        f"Invalid logging level {str(level)} or out of range. "
        "Keep within KISS principle"
    )

    # Process errors first
    # #####################

    if not check_level(level):
        # Why not?
        if isinstance(level, logging.Logger):  # pragma: no cover
            pass
        elif isinstance(level, int):
            if level not in logging.getLevelNamesMapping().values() and (
                (level > 0 and level < 50) or level < 0 or level > 50
            ):
                # Although valid, KISS principle
                # or out of range
                raise ValueError(msg_valueerror_int)
            else:  # pragma: no cover
                pass
        elif isinstance(level, str):
            is_str_convertable = str2int(level=level)
            if isinstance(is_str_convertable, int) and level not in map(
                str, logging.getLevelNamesMapping().values()
            ):
                if is_str_convertable > 0 and is_str_convertable < 50:
                    raise ValueError(msg_valueerror_str)
                elif is_str_convertable < 0:
                    raise ValueError(msg_valueerror_str)
                elif is_str_convertable > 50:
                    raise ValueError(msg_valueerror_str)
                else:  # pragma: no cover
                    pass
            else:  # pragma: no cover
                pass
        else:
            raise TypeError(msg_typerror)
    else:  # pragma: no cover
        pass

    if is_assume_root(level):
        """Guess referring to root logger. Avoid making a disasterous
        assumption with horrible side effects"""
        root_ = logging.getLogger("root")
        level_name = logging.getLevelName(root_.getEffectiveLevel())
    else:
        if isinstance(level, logging.Logger):
            level_name = logging.getLevelName(level.getEffectiveLevel())
        elif isinstance(level, str):
            if level in map(str, logging.getLevelNamesMapping().values()):
                level_name = logging.getLevelName(int(level))
            elif level in logging.getLevelNamesMapping().keys():
                level_name = level
            else:  # pragma: no cover
                raise ValueError(msg_valueerror_str)
        elif isinstance(level, int):
            if level in logging.getLevelNamesMapping().values():
                level_name = logging.getLevelName(level)
            else:  # pragma: no cover
                raise ValueError(msg_valueerror_int)
        else:  # pragma: no cover Check unsupported type already occurred
            raise TypeError(msg_typerror)

    return level_name


def _normalize_level_name(logger_name):
    """For
    :py:func:`logging_strict.tech_niques.logging_capture.captureLogs`,
    normalize level names

    :param logger_name:

       Logger name can be a :py:class:`logging.Logger`, str

    :type logger_name: typing.Any | None
    :returns: Normalized logger level name
    :rtype: str
    :raises:

       - :py:exc:`TypeError` -- logger name is unsupported type

    """
    if is_assume_root(logger_name):
        # None or empty string (after strip)
        # root logger
        logger_ = logging.getLogger("root")
    else:
        if isinstance(logger_name, logging.Logger):
            logger_ = logger_name
        elif isinstance(logger_name, str):
            logger_ = logging.getLogger(logger_name)
        else:
            msg = "logger name is unsupported type. Cannot get level name"
            raise TypeError(msg)

    level = logger_.getEffectiveLevel()
    level_name = logging.getLevelName(level)

    return level_name


def _normalize_logger(logger):
    """Ensure working with a :py:class:`logger.Logger`

    :param logger:

       Logger name can be a :py:class:`logging.Logger` or str

    :type logger: logging.Logger | str | None
    :returns: Normalized logger
    :rtype: logging.Logger

    :raises:

       - :py:exc:`TypeError` -- logging module requires logger name to be a str

    .. note::

       :py:func:`logging.getLogger` requires logger
       name to be a str or :py:exc:`TypeError` occurs

    """
    _logger_name = logger
    if is_assume_root(_logger_name):
        # Assume root as the logging module does
        _logger = logging.getLogger()
    else:
        if isinstance(_logger_name, logging.Logger):
            _logger = _logger_name
        elif is_ok(_logger_name):
            _logger = logging.getLogger(_logger_name)
        else:
            msg = "A logger name must be a string"
            raise TypeError(msg)

    return _logger


def _normalize_formatter(format_=LOG_FORMAT):
    """Retrieve logging.Formatter from user input

    :param format_:

       Default :py:data:`logging_strict.constants.LOG_FORMAT`

       Can pass in anything. Intended to be a logging format str

    :type format_: typing.Any | None
    :returns: Valid logging formatter to be added to a logging.Handler
    :rtype: logging.Formatter
    """
    if format_ is None or is_not_ok(format_):
        format_str = LOG_FORMAT
    else:
        format_str = format_

    if check_formatter(format_=format_str):
        ret = logging.Formatter(format_str)
    else:
        """Invalid logging.Formatter str, use fallback

        Prevents having to raise ValueError or TypeError"""
        ret = logging.Formatter(LOG_FORMAT)

    return ret


@attrs.define
class _LoggingWatcher:
    """Replaces collections.namedtuple"""

    records: MutableSequence[logging.LogRecord] = attrs.field(
        factory=list,
        kw_only=False,
        validator=attrs.validators.deep_iterable(
            member_validator=attrs.validators.instance_of(logging.LogRecord),
            iterable_validator=attrs.validators.instance_of(list),
        ),
    )
    output: MutableSequence[str] = attrs.field(
        factory=list,
        kw_only=False,
        validator=attrs.validators.deep_iterable(
            member_validator=attrs.validators.instance_of(str),
            iterable_validator=attrs.validators.instance_of(list),
        ),
    )

    def getHandlerByName(self, name):
        """Get a handler with the specified *name*, or None if there
        isn't one with that name.

        :param name: handler function name
        :type name: str
        :returns: A logging handler func
        :rtype: type[logging.Handler]
        """
        return logging.getHandlerByName(name)

    def getHandlerNames(self):
        """Return all known handler names as an immutable set

        :returns: Handler function names
        :rtype: frozenset[str]
        """
        return logging.getHandlerNames()

    def getLevelNo(self, level_name):
        """Get Logging level number, given a logging level name

        :param level_name: logging level name
        :type level_name: str
        :returns: Logging level integer
        :rtype: int | None
        """
        mapping = logging.getLevelNamesMapping()
        if level_name in mapping.keys():
            ret = mapping[level_name]
        else:
            ret = None

        return ret


class _CapturingHandler(logging.Handler):
    """A logging handler capturing all (raw and formatted) logging output."""

    def __init__(self):
        """Class constructor"""
        logging.Handler.__init__(self)
        self.watcher = _LoggingWatcher([], [])

    def flush(self):  # pragma: no cover No way to test this. No side effect(s)
        """Flush records"""
        self.watcher.records.clear()
        self.watcher.output.clear()

    def emit(self, record):
        """Save record. Format/Save message

        :param record: logging record. Save as record and as str message
        :type record: logging.LogRecord
        """
        self.watcher.records.append(record)
        msg = self.format(record)
        self.watcher.output.append(msg)


@attrs.define
class _LoggerStoredState:
    """Stores logger state

    :ivar level_name: logging level name
    :vartype level_name: str
    :ivar propagate: True to propagate logging errors
    :vartype propagate: bool
    :ivar handlers: logging handlers
    :vartype handlers: list[type[logging.Handler]]
    """

    level_name: str = attrs.field(kw_only=False)
    propagate: bool = attrs.field(kw_only=False)
    handlers: list[type[logging.Handler]] = attrs.field(
        kw_only=False,
        factory=list,
        validator=attrs.validators.deep_iterable(
            member_validator=attrs.validators.instance_of(logging.Handler),
            iterable_validator=attrs.validators.instance_of(list),
        ),
    )


@contextlib.contextmanager
def captureLogs(
    logger=None,
    level=None,
    format_=LOG_FORMAT,
):
    """A context manager to capture logging a loggers logging output

    Example::

        import logging
        from logging_strict.tech_niques import captureLogs

        with captureLogs('foo', level='INFO') as cm:
            logging.getLogger('foo').info('first message')
            logging.getLogger('foo.bar').error('second message')
        print(cm.output)

    The watcher (
    :py:class:`logging_strict.tech_niques.logging_capture._LoggingWatcher`
    ) has attributes:

    - output

    - records

      unformatted records


    :param logger: Default ``None``. logger or logger name
    :type logger: str | logging.Logger | None
    :param level: Default ``None``. Logging level
    :type level: str | int | None
    :param format_: Default ``None``. Can override logging format spec
    :type format_: str | None
    :returns:

       Context manager yields one
       :py:class:`logging_strict.tech_niques.logging_capture._LoggingWatcher`.
       Which stores the log records/messages

    :rtype: Iterator[logging_strict.tech_niques.logging_capture._LoggingWatcher]

    .. seealso::

       Context manager howto, :pep:`343`


    """
    # __init__
    # ############
    # Raises ValueError if invalid logging format str
    formatter = _normalize_formatter(format_=format_)

    # Raises ValueError and TypeError
    _level = _normalize_level(level)

    # Raises TypeError
    _logger = _normalize_logger(logger)

    try:
        # __enter__
        # ############
        #    _level from params
        handler = _CapturingHandler()
        handler.setLevel(_level)
        handler.setFormatter(formatter)

        #    str, not an int
        logger_stored_state = _LoggerStoredState(
            level_name=_normalize_level_name(_logger),
            propagate=_logger.propagate,
            handlers=_logger.handlers[:],
        )

        """
        _old_level = _normalize_level_name(_logger)
        _old_handlers = _logger.handlers[:]
        _old_propagate = _logger.propagate
        """
        pass

        _logger.handlers = [handler]
        _logger.setLevel(_level)
        _logger.propagate = False

        yield handler.watcher
    except Exception:
        # let unexpected exceptions pass through
        raise
    finally:
        # __exit__
        # ############
        #    Restore state
        _logger.handlers = logger_stored_state.handlers
        _logger.propagate = logger_stored_state.propagate
        _logger.setLevel(logger_stored_state.level_name)
        del logger_stored_state


@contextlib.contextmanager
def captureLogsMany(
    loggers=(),
    levels=(),
    format_=LOG_FORMAT,
):
    """Behave exactly like
    :py:func:`~logging_strict.tech_niques.logging_capture.captureLogs`
    except intended for multiple loggers rather than one

    :param loggers: Sequence of loggers
    :type loggers: Sequence[str | logging.Logger]
    :param levels: Sequence of levels corresponding to each loggers in order
    :type levels: Sequence[str | int | None]
    :param format_: Default ``None``. Can override logging format spec
    :type format_: str | None
    :returns:

       Context manager yields all
       :py:class:`logging_strict.tech_niques.logging_capture._LoggingWatcher`.
       in a tuple. Order maintained

    :rtype: Iterator[tuple[logging_strict.tech_niques.logging_capture._LoggingWatcher]]
    :raises:

       - :py:exc:`AssertionError` -- Loggers and levels count mismatch

    """
    # __init__
    formatter = _normalize_formatter(format_=format_)

    assert len(loggers) == len(levels)

    # Normalize levels. :paramref:`levels` is possibly immutable
    _levels = []
    for idx, level in enumerate(levels):
        _levels.append(_normalize_level(level))

    # Normalize loggers
    _loggers = []
    for logger in loggers:
        _loggers.append(_normalize_logger(logger))

    try:
        # __enter__
        save_state = []
        ret = []
        for idx, _logger in enumerate(_loggers):
            # Get desired level for this logger
            _level = _levels[idx]

            # Save previous state
            save_state.append(
                _LoggerStoredState(
                    level_name=_normalize_level_name(_logger),
                    propagate=_logger.propagate,
                    handlers=_logger.handlers[:],
                ),
            )

            # Create handler
            handler_x = _CapturingHandler()
            handler_x.setLevel(_level)
            handler_x.setFormatter(formatter)

            _logger.handlers = [handler_x]
            _logger.setLevel(_level)
            _logger.propagate = False

            ret.append(handler_x.watcher)

        yield tuple(ret)
    except Exception:
        # let unexpected exceptions pass through
        raise
    finally:
        # __exit__
        for idx, logger in enumerate(loggers):
            logger_stored_state = save_state[idx]
            # Normalize loggers
            _logger = _normalize_logger(logger)

            #    Restore state
            _logger.handlers = logger_stored_state.handlers
            _logger.propagate = logger_stored_state.propagate
            _logger.setLevel(logger_stored_state.level_name)
        del logger_stored_state, _logger, save_state, ret
