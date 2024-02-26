.. _api_synchronous_logging:

====================
Synchronous logging
====================

unittest redirects :py:obj:`sys.stderr` and :py:obj:`sys.stdout`. Logging needs
access to the redirected streams. Without this fix, the log messages won't be
shown

To see third-party log messages replace :code:`logging.basicConfig` statement.
Instead, to see root messages, initialize logging and include handlers

.. code-block:: python

    import logging
    import sys
    import unittest
    from logging_strict.constants import LOG_FORMAT, g_app_name
    from logging_strict.tech_niques import LoggerRedirector


    class SomeUnittestClass(unittest.TestCase):
        def setUp(self):
            package_name = g_app_name  # replace with your package name
            g_module_name = "test_docs_sync_log_capture"
            g_module = f"{package_name}.tests.tech_niques.{g_module_name}"
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
            LoggerRedirector.reset_loggers(
                fake_stdout=sys.stdout,
                fake_stderr=sys.stderr,
            )

        def test_logging_redirecting(self):
            # self._LOGGER.info("Is this shown?")
            # ^^ uncomment ^^
            pass


    if __name__ == "__main__":  # pragma: no cover
        unittest.main(tb_locals=True)

Before running this unittest, uncomment out the lines preceding the
comment, ``# ^^ uncomment ^^``

.. code-block:: shell

   python -m tests.tech_niques.test_docs_sync_log_capture

Expected output

.. code-block:: text

   $> python -m tests.test_docs_sync_log_capture
   INFO test_docs_sync_log_capture test_logging_redirecting: *: Is this shown?
   .
   ----------------------------------------------------------------------
   Ran 1 test in 0.000s

   OK
