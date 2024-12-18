"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

Check logging deals with confirming logging level int and logging level name.

"""

import logging
import unittest

from logging_strict.constants import (
    LOG_FMT_DETAILED,
    LOG_FMT_SIMPLE,
    LOG_FORMAT,
    g_app_name,
)
from logging_strict.util.check_logging import (
    check_formatter,
    check_level,
    check_level_name,
    check_logger,
    is_assume_root,
    str2int,
)


class LoggingChecks(unittest.TestCase):
    """Various logging attributes checks"""

    def test_str2int(self):
        """Convert a numeric str --> int"""
        valids = (
            "11",
            "49",
            "51",
            "-1",
            "1",
        )
        for valid in valids:
            self.assertIsInstance(valid, str)
            mixed_out = str2int(valid)
            self.assertNotIsInstance(mixed_out, bool)
            self.assertIsInstance(mixed_out, int)
            self.assertEqual(mixed_out, int(valid))

        invalids = (
            "",
            "     ",
            "INFO",
            "12.5",
        )
        for invalid in invalids:
            self.assertIsInstance(invalid, str)
            mixed_out = str2int(invalid)
            self.assertIsInstance(mixed_out, bool)
            self.assertFalse(mixed_out)

        invalids = (None,)
        for invalid in invalids:
            mixed_out = str2int(invalid)
            self.assertIsInstance(mixed_out, bool)
            self.assertFalse(mixed_out)

    def test_is_assume_root(self):
        """Check can recognize root logger"""
        invalids = (
            0.12345,
            24,
            0,
            "0",
        )
        for invalid in invalids:
            self.assertFalse(is_assume_root(invalid))

        # These are all considered to mean root logger
        valids = (
            None,
            "",
            "      ",
            "root",
        )
        for valid in valids:
            self.assertTrue(is_assume_root(valid))

    def test_check_logger(self):
        """Check would produce a logging.Logger"""

        # Anything considered root
        valids = (
            None,
            "",
            "      ",
            "root",
        )
        for valid in valids:
            self.assertTrue(check_logger(valid))

        # logger or non-empty stripped str
        valids = (
            "foo",
            "foo.bar.baz",
            g_app_name,
            logging.Logger("root"),
            logging.Logger(g_app_name),
        )
        for valid in valids:
            self.assertTrue(check_logger(valid))

        # Unsupported type
        invalids = (
            0.12345,
            15,
        )
        for invalid in invalids:
            self.assertFalse(check_logger(invalid))

    def test_check_level_name(self):
        """Check would produce a logging level name"""
        # Anything considered root
        valids = (
            None,
            "",
            "      ",
            "root",
        )
        for valid in valids:
            self.assertTrue(check_level_name(valid))

        valids = (
            "foo",
            "foo.baz",
            g_app_name,
            "s,a*d&f#as%df",
            logging.getLogger("root"),
            logging.getLogger(g_app_name),
        )
        for valid in valids:
            self.assertTrue(check_level_name(valid))

        invalids = (
            0.12345,
            15,
        )
        for invalid in invalids:
            self.assertFalse(check_level_name(invalid))

    def test_check_level(self):
        """Check the check of checking logging level"""
        # Assume root logger
        roots = (
            "",
            None,
            "       ",
            "root",
        )
        for root_ in roots:
            actual_level_name = check_level(root_)
            self.assertTrue(actual_level_name)

        # logger.Logger
        logger_app = logging.getLogger(g_app_name)
        self.assertTrue(check_level(logger_app))
        log_foo = logging.getLogger("foo")
        self.assertTrue(check_level(log_foo))

        # int
        # ###############
        # Invalid int. 1 < x < 49
        invalids = (
            11,  # KISS principle
            49,  # KISS principle
            51,  # out of range
            -1,
            1,
        )
        for invalid in invalids:
            self.assertFalse(check_level(invalid))

        valids = (
            logging.NOTSET,
            logging.DEBUG,
            logging.INFO,
            logging.WARNING,
            logging.ERROR,
            logging.CRITICAL,
            logging.FATAL,  # Same as CRITICAL
        )
        for valid in valids:
            actual_level_name = check_level(valid)
            self.assertTrue(check_level(valid))

        # str
        # ###############
        # Invalid int. 1 < x < 49
        invalids = (
            "11",  # KISS principle
            "49",  # KISS principle
            "51",  # out of range
            "-1",  # out of range
            "1",  # KISS principle
        )
        for invalid in invalids:
            self.assertFalse(check_level(invalid))

        valids = (
            "0",
            "10",
            "20",
            "30",
            "40",
            "50",
        )
        for valid in valids:
            self.assertTrue(check_level(valid))

        valids = (
            "NOTSET",
            "DEBUG",
            "INFO",
            "WARN",
            "WARNING",
            "ERROR",
            "CRITICAL",
            "FATAL",
        )
        for valid in valids:
            self.assertTrue(check_level(valid))

        invalids = ("dsafsadfadsf",)
        for invalid in invalids:
            self.assertFalse(check_level(invalid))

        # Unsupported type
        # ##################
        invalids = (11.4,)
        for invalid in invalids:
            self.assertFalse(check_level(invalid))

    def test_check_formatter(self):
        """Check logging.Formatter would like"""
        # None, empty ish str, unsupported type
        invalids = (
            None,
            "",
            "      ",
            0.12345,
            14,
        )
        for invalid in invalids:
            self.assertFalse(check_formatter(invalid))

        # logging.Formatter likes. All log formats used in this app
        valids = (
            LOG_FORMAT,
            LOG_FMT_DETAILED,
            LOG_FMT_SIMPLE,
        )
        for valid in valids:
            self.assertTrue(check_formatter(valid))

        # logging.Formatter not like
        invalids = ("asdf %q sadf ",)
        for invalid in invalids:
            self.assertFalse(check_formatter(invalid))


if __name__ == "__main__":  # pragma: no cover
    """
    .. code-block:: shell

       python -m tests.test_check_logging --locals

       python -m unittest tests.test_check_logging \
       -k LoggingChecks.test_is_assume_root --locals

       python -m unittest tests.test_check_logging \
       -k LoggingChecks.test_str2int --locals

       coverage erase --data-file=".coverage-combine-32"

       coverage run --data-file=".coverage-combine-32" \
       -m unittest discover -t. -s tests -p "test_check_logging*.py" --locals

       coverage report --include="*check_logging*" --no-skip-covered \
       --data-file=".coverage-combine-32"
    """
    unittest.main(tb_locals=True)
