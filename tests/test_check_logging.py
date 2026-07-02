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

    def test_str2int(self) -> None:
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

        invalids_0 = (
            "",
            "     ",
            "INFO",
            "12.5",
        )
        for invalid_0 in invalids_0:
            self.assertIsInstance(invalid_0, str)
            mixed_out = str2int(invalid_0)
            self.assertIsInstance(mixed_out, bool)
            self.assertFalse(mixed_out)

        invalids_1 = (None,)
        for invalid_1 in invalids_1:
            mixed_out = str2int(invalid_1)
            self.assertIsInstance(mixed_out, bool)
            self.assertFalse(mixed_out)

    def test_is_assume_root(self) -> None:
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

    def test_check_logger(self) -> None:
        """Check would produce a logging.Logger"""

        # Anything considered root
        valids_0 = (
            None,
            "",
            "      ",
            "root",
        )
        for valid_0 in valids_0:
            self.assertTrue(check_logger(valid_0))

        # logger or non-empty stripped str
        valids_1 = (
            "foo",
            "foo.bar.baz",
            g_app_name,
            logging.Logger("root"),
            logging.Logger(g_app_name),
        )
        for valid_1 in valids_1:
            self.assertTrue(check_logger(valid_1))

        # Unsupported type
        invalids_2 = (
            0.12345,
            15,
        )
        for invalid_2 in invalids_2:
            self.assertFalse(
                check_logger(
                    invalid_2,  # type: ignore[arg-type]
                )
            )

    def test_check_level_name(self) -> None:
        """Check would produce a logging level name"""
        # Anything considered root
        valids_0 = (
            None,
            "",
            "      ",
            "root",
        )
        for valid_0 in valids_0:
            self.assertTrue(check_level_name(valid_0))

        valids_1 = (
            "foo",
            "foo.baz",
            g_app_name,
            "s,a*d&f#as%df",
            logging.getLogger("root"),
            logging.getLogger(g_app_name),
        )
        for valid_1 in valids_1:
            self.assertTrue(check_level_name(valid_1))

        invalids_2 = (
            0.12345,
            15,
        )
        for invalid_2 in invalids_2:
            self.assertFalse(check_level_name(invalid_2))

    def test_check_level(self) -> None:
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
        invalids_0 = (
            11,  # KISS principle
            49,  # KISS principle
            51,  # out of range
            -1,
            1,
        )
        for invalid_0 in invalids_0:
            self.assertFalse(check_level(invalid_0))

        valids_0 = (
            logging.NOTSET,
            logging.DEBUG,
            logging.INFO,
            logging.WARNING,
            logging.ERROR,
            logging.CRITICAL,
            logging.FATAL,  # Same as CRITICAL
        )
        for valid_0 in valids_0:
            actual_level_name = check_level(valid_0)
            self.assertTrue(check_level(valid_0))

        # str
        # ###############
        # Invalid int. 1 < x < 49
        invalids_1 = (
            "11",  # KISS principle
            "49",  # KISS principle
            "51",  # out of range
            "-1",  # out of range
            "1",  # KISS principle
        )
        for invalid_1 in invalids_1:
            self.assertFalse(check_level(invalid_1))

        valids_1 = (
            "0",
            "10",
            "20",
            "30",
            "40",
            "50",
        )
        for valid_1 in valids_1:
            self.assertTrue(check_level(valid_1))

        valids_2 = (
            "NOTSET",
            "DEBUG",
            "INFO",
            "WARN",
            "WARNING",
            "ERROR",
            "CRITICAL",
            "FATAL",
        )
        for valid_2 in valids_2:
            self.assertTrue(check_level(valid_2))

        invalids_2 = ("dsafsadfadsf",)
        for invalid_2 in invalids_2:
            self.assertFalse(check_level(invalid_2))

        # Unsupported type
        # ##################
        invalids_3 = (11.4,)
        for invalid_3 in invalids_3:
            self.assertFalse(check_level(invalid_3))

    def test_check_formatter(self) -> None:
        """Check logging.Formatter would like"""
        # None, empty ish str, unsupported type
        invalids_0 = (
            None,
            "",
            "      ",
            0.12345,
            14,
        )
        for invalid_0 in invalids_0:
            self.assertFalse(check_formatter(invalid_0))

        # logging.Formatter likes. All log formats used in this app
        valids = (
            LOG_FORMAT,
            LOG_FMT_DETAILED,
            LOG_FMT_SIMPLE,
        )
        for valid in valids:
            self.assertTrue(check_formatter(valid))

        # logging.Formatter not like
        invalids_1 = ("asdf %q sadf ",)
        for invalid_1 in invalids_1:
            self.assertFalse(check_formatter(invalid_1))


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
