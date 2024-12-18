"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

..

In unittest class, redirect stdout/stderr. Essential for synchronous logging

.. py:data: __all__
   :type: tuple[str]
   :value: ("LoggerRedirector",)

   This module exports

"""

import logging
import sys

__all__ = ("LoggerRedirector",)


class LoggerRedirector:  # pragma: no cover
    """:mod:`unittest` redirects :code:`sys.stdout` and
    :code:`sys.stderr`. Keep a reference to the real streams so we can
    later be reverted. Logging goes to the wrong IO streams. Upon
    failure, there are no log messages.

    Redirect to the correct IO streams.

    Required for the unittest discover command: ``--buffer``
    option

    .. py:attribute:: _real_stdout
       :noindex:

       Hold :py:data:`sys.stdout` reference. Restores sys.stdout at the end of the
       context manager

    .. py:attribute:: _real_stderr
       :noindex:

       Hold :py:data:`sys.stderr` reference. Restores sys.stdout at the end of the
       context manager

    Usage

    In a unittest module (level), setup
    :code:`logging.basicConfig`

    >>> import sys
    >>> import logging
    >>> logging.basicConfig(
    ...     format='%(module)s %(levelname)s: %(message)s',
    ...     level=logging.INFO,
    ...     stream=sys.stdout,
    ... )

    In a unittest module class

    .. doctest::
       :options: +SKIP

       import sys
       import logging
       from logging_strict.tech_niques import LoggerRedirector
       def setUp(self):
           # unittest has reassigned sys.stdout and sys.stderr by this point

           g_module = f"[app_name].tests.test_[module name]"
           self._LOGGER = logging.getLogger(g_module)

           # %(asctime)s
           logging.basicConfig(
                format="%(levelname)s %(module)s: %(message)s",
                level=logging.INFO,
                stream=sys.stdout,
           )
           LoggerRedirector.redirect_loggers(
               fake_stdout=sys.stdout,
               fake_stderr=sys.stderr,
           )
       def tearDown(self):
           # unittest will revert sys.stdout and sys.stderr after this
           LoggerRedirector.reset_loggers(
               fake_stdout=sys.stdout,
               fake_stderr=sys.stderr,
           )


    .. seealso::

       `LoggerRedirector source <https://stackoverflow.com/a/69202374>`_

       `LoggerRedirector author <https://stackoverflow.com/users/6248563/satyen-a>`_

       In unittests, showing log messages
       `on failure <https://stackoverflow.com/q/69200881>`_


    """

    _real_stdout = sys.stdout
    _real_stderr = sys.stderr

    @staticmethod
    def all_loggers():  # pragma: no cover
        """Get loggers

        :returns: space separated tests (method name(s))
        :rtype: Sequence[logging.Logger]
        """
        loggers = [logging.getLogger()]
        loggers += [logging.getLogger(name) for name in logging.root.manager.loggerDict]

        return loggers

    @classmethod
    def redirect_loggers(
        cls,
        fake_stdout=None,
        fake_stderr=None,
    ) -> None:  # pragma: no cover
        """unittest temporarily switch the IO streams. Use the unittest
        temporary IO streams

        Call in unittest class setUp method

        :param fake_stdout: unittest temporary stdout IO stream
        :type fake_stdout: typing.TextIO
        :param fake_stderr: unittest temporary stderr IO stream
        :type fake_stderr: typing.TextIO
        """
        if (not fake_stdout or fake_stdout is cls._real_stdout) and (
            not fake_stderr or fake_stderr is cls._real_stderr
        ):
            return
        for logger in cls.all_loggers():
            for handler in logger.handlers:
                if hasattr(handler, "stream"):
                    if handler.stream is cls._real_stdout:
                        handler.setStream(fake_stdout)
                    if handler.stream is cls._real_stderr:
                        handler.setStream(fake_stderr)

    @classmethod
    def reset_loggers(
        cls,
        fake_stdout=None,
        fake_stderr=None,
    ) -> None:  # pragma: no cover
        """unittest temporarily switch the IO streams. Switch back to
        the normal IO streams

        Call in unittest class tearDown method

        :param fake_stdout: unittest temporary stdout IO stream
        :type fake_stdout: typing.TextIO
        :param fake_stderr: unittest temporary stderr IO stream
        :type fake_stderr: typing.TextIO
        """
        if (not fake_stdout or fake_stdout is cls._real_stdout) and (
            not fake_stderr or fake_stderr is cls._real_stderr
        ):
            return
        for logger in cls.all_loggers():
            for handler in logger.handlers:
                if hasattr(handler, "stream"):
                    if handler.stream is fake_stdout:
                        handler.setStream(cls._real_stdout)
                    if handler.stream is fake_stderr:
                        handler.setStream(cls._real_stderr)
