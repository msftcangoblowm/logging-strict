.. _api_capture_logging:

Capture logging
===============

In this code sample, package ``foo`` level ``INFO`` and above log
messages are captured and available in cm.output as a ``list[str]``

.. testcode::

    import logging
    import unittest
    from logging_strict.tech_niques import captureLogs
    from logging_strict.constants import LOG_FORMAT


    class SuppressPackageLogging(unittest.TestCase):
        def test_logging_capture(self):
            """Docs example. Confirms levelname and message, not others"""
            msg0 = 'first msg'
            msg1 = 'second msg'
            # "%(levelname)s %(module)s %(funcName)s: %(lineno)d: %(message)s"
            with captureLogs('foo', level='INFO', format_=LOG_FORMAT) as cm:
                logging.getLogger('foo').info(msg0)
                logging.getLogger('foo.bar').error(msg1)

            out = cm.output
            self.assertIsInstance(out, list)
            self.assertEqual(len(out), 2)
            line0 = out[0]
            line1 = out[1]
            # Confirm levelname
            self.assertIn("INFO", line0)
            self.assertIn("ERROR", line1)
            # Confirm message
            self.assertIn(msg0, line0)
            self.assertIn(msg1, line1)


    if __name__ == "__main__":  # pragma: no cover
        unittest.main(tb_locals=True)

.. testoutput:
   :options: +ELLIPSIS, +NORMALIZE_WHITESPACE
   .
   ----------------------------------------------------------------------
   Ran 1 test in *s

   OK
