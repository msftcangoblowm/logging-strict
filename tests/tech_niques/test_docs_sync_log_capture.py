"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

Demonstrate synchronous logging capture

This test appears in the docs, :ref:`api/logging/api_logging_synchronous:synchronous logging`

Uncomment lines starting with ``# ^^ uncomment ^^`` then run this test

Reasons these are commented out:

- SPAM. The logging message will appear when during :command:`run coverage`

- ``logging.basicConfig`` call is destructive. OK only when this one unittest
  is run by itself. Not ok when running within testing app or by coverage

"""

import logging
import sys
import unittest

from logging_strict.constants import LOG_FORMAT  # noqa: F401
from logging_strict.constants import g_app_name
from logging_strict.tech_niques import LoggerRedirector


class SomeUnittestClass(unittest.TestCase):
    """Example straight from the docs. Applicable to unittest, not pytest"""

    def setUp(self):
        """Setup loggers redirect"""
        g_module_name = "test_docs_sync_log_capture"
        g_module = f"{g_app_name}.tests.tech_niques.{g_module_name}"

        self._LOGGER = logging.getLogger(g_module)

        # So see root logging messages, replace, needs logging with handlers
        """
        logging.basicConfig(
            format=LOG_FORMAT,
            level=logging.INFO,
            stream=sys.stdout,
        )
        """
        # ^^ uncomment ^^
        pass

        LoggerRedirector.redirect_loggers(
            fake_stdout=sys.stdout,
            fake_stderr=sys.stderr,
        )

    def tearDown(self):
        """Restore previous state for sys.stderr and sys.stdout"""
        LoggerRedirector.reset_loggers(
            fake_stdout=sys.stdout,
            fake_stderr=sys.stderr,
        )

    def test_logging_redirect(self):
        """Are log messages shown? Uncomment self._LOGGER.info line then run

        Confirm log message printed

        .. code-block:: text

           INFO test_docs_sync_log_capture test_logging_redirecting: *: Is this shown?

        """
        # self._LOGGER.info("Is this shown?")
        # ^^ uncomment ^^
        pass

        # self.assertTrue(False)
        # In separate test try, ^^ uncomment ^^
        pass


if __name__ == "__main__":  # pragma: no cover
    """In synchronous unittest (class), capture logging

    The **purpose** of this unittest is to
    **demonstrate this redirect logging technique**, not to test a source module.

    Before running this unittest, comments ``# ^^ uncomment ^^`` and
    uncomment preceding commented out lines

    Then can run the unittest, from package base folder

    .. code-block:: shell

       python -m tests.tech_niques.test_docs_sync_log_capture


    Output

    .. code-block:: text

       $> python -m tests.tech_niques.test_docs_sync_log_capture
       INFO test_docs_sync_log_capture test_logging_redirecting: *: Is this shown?
       .
       ----------------------------------------------------------------------
       Ran 1 test in 0.000s

       OK

    """
    unittest.main(tb_locals=True)
