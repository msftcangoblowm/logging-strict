"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

Test logging-strict main entrypoint.

"""

import argparse
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import (
    Mock,
    patch,
)

from logging_strict import LoggingConfigCategory
from logging_strict.constants import g_app_name
from logging_strict.ep_validate_yaml import (
    _process_args,
    main,
)
from logging_strict.logging_yaml_abc import YAML_LOGGING_CONFIG_SUFFIX

if sys.version_info >= (3, 9):  # pragma: no cover
    from collections.abc import Sequence
else:  # pragma: no cover
    from typing import Sequence


class EntrypointStrictYAMLValidate(unittest.TestCase):
    """Test entrypoint for strict yaml validation."""

    def setUp(self):
        """Initialize variables for tests base folder and cwd."""
        if "__pycache__" in __file__:
            # cached
            path_tests = Path(__file__).parent.parent
        else:
            # not cached
            path_tests = Path(__file__).parent
        self.path_cwd = path_tests.parent
        self.package = g_app_name
        self.path_package_src = self.path_cwd.joinpath("src", g_app_name)
        self.package_data_folder_start = "configs"

    def test_process_args(self):
        """Test out interface. Bypass calling the entrypoint"""
        # 1, 2, 3, 5, 10
        # No arguments --> exit code 3
        argument = Mock()  # argument
        argument.option_strings = (
            "Bob arbitrarily decided supporting defaulting to the cwd is nonsense",
        )
        message = "Well this is embarrassing, Bob rejected your transaction"
        with (
            patch(
                "argparse.ArgumentParser.parse_args",
                side_effect=argparse.ArgumentError(argument, message),
            ),
            self.assertRaises(SystemExit) as cm,
        ):
            _process_args()
        exc = cm.exception
        self.assertIsInstance(exc.code, int)
        self.assertEqual(exc.code, 3)

        # Extra args exit code 5
        with (
            patch(
                "argparse.ArgumentParser.parse_args",
                return_value=argparse.Namespace(
                    **{
                        "dir": self.path_package_src,
                        "package": self.package,
                        "package_data_folder_start": self.package_data_folder_start,
                        "category": LoggingConfigCategory.UI.value,
                        "genre": "textual",
                        "flavor": "asz",
                        "version": "1",
                        "fail_fast": True,
                        "an_extra_kwarg": True,
                    },
                ),
            ),
            self.assertRaises(SystemExit) as cm,
        ):
            _process_args()
        exc = cm.exception
        self.assertIsInstance(exc.code, int)
        self.assertEqual(exc.code, 5)

        # exit code 6 no package (academic cuz fallback)
        valids = (
            {
                "dir": self.path_package_src,
                "package": None,
                "package_data_folder_start": self.package_data_folder_start,
                "category": LoggingConfigCategory.UI.value,
                "genre": "textual",
                "flavor": "asz",
                "version": "1",
                "fail_fast": True,
            },
            {
                "dir": self.path_package_src,
                "package_data_folder_start": self.package_data_folder_start,
                "category": LoggingConfigCategory.UI.value,
                "genre": "textual",
                "flavor": "asz",
                "version": "1",
                "fail_fast": True,
            },
        )
        for kwargs in valids:
            with (
                patch(
                    "argparse.ArgumentParser.parse_args",
                    return_value=argparse.Namespace(**kwargs),
                ),
                self.assertRaises(SystemExit) as cm,
            ):
                _process_args()
            exc = cm.exception
            self.assertIsInstance(exc.code, int)
            self.assertEqual(exc.code, 6)

        # Exit code 7 No package_data_folder_start (academic cuz fallback)
        valids = (
            {
                "dir": self.path_package_src,
                "package": self.package,
                "package_data_folder_start": None,
                "category": LoggingConfigCategory.UI.value,
                "genre": "textual",
                "flavor": "asz",
                "version": "1",
                "fail_fast": True,
            },
            {
                "dir": self.path_package_src,
                "package": self.package,
                "category": LoggingConfigCategory.UI.value,
                "genre": "textual",
                "flavor": "asz",
                "version": "1",
                "fail_fast": True,
            },
        )
        for kwargs in valids:
            with (
                patch(
                    "argparse.ArgumentParser.parse_args",
                    return_value=argparse.Namespace(**kwargs),
                ),
                self.assertRaises(SystemExit) as cm,
            ):
                _process_args()
            exc = cm.exception
            self.assertIsInstance(exc.code, int)
            self.assertEqual(exc.code, 7)

        # All files
        # Category dodgy --> All categories
        dodgy_categories = (
            (None, None),
            (0.12345, None),
            ("notacategory", None),  # not in category enum --> None --> all results
        )
        for category, genre in dodgy_categories:
            with (
                patch(
                    "argparse.ArgumentParser.parse_args",
                    return_value=argparse.Namespace(
                        **{
                            "dir": self.path_package_src,
                            "package": self.package,
                            "package_data_folder_start": self.package_data_folder_start,
                            "category": category,  # all category
                            "genre": genre,  # all genre
                            "flavor": "asz",
                        },
                    ),
                ),
            ):
                paths_file, is_fail_fast = _process_args()
                self.assertIsInstance(paths_file, Sequence)
                file_count = len(paths_file)
                self.assertEqual(file_count, 2)
                self.assertIsInstance(is_fail_fast, bool)
                self.assertEqual(is_fail_fast, True)

        # No results
        dodgy_categories = ((None, "bob"),)
        for category, flavor in dodgy_categories:
            with (
                patch(
                    "argparse.ArgumentParser.parse_args",
                    return_value=argparse.Namespace(
                        **{
                            "dir": self.path_package_src,
                            "package": self.package,
                            "package_data_folder_start": self.package_data_folder_start,
                            "category": category,  # all category
                            "genre": None,  # all genre
                            "flavor": flavor,
                        },
                    ),
                ),
                self.assertRaises(SystemExit) as cm,
            ):
                _process_args()
            exc = cm.exception
            self.assertIsInstance(exc.code, int)
            self.assertEqual(exc.code, 10)

        # Success -- implict optional kwargs
        valids = (
            (
                {  # configs: 1
                    "dir": self.path_package_src,
                    "package": self.package,
                    "package_data_folder_start": self.package_data_folder_start,
                    "category": LoggingConfigCategory.UI.value,
                },
                1,
            ),
            (
                {  # bad_idea/folder0: 1, bad_idea/folder1: 1, configs: 2
                    "dir": self.path_package_src,
                    "package": self.package,
                    "package_data_folder_start": self.package_data_folder_start,
                },
                4,
            ),
        )
        for kwargs, file_count_expected in valids:
            with (
                patch(
                    "argparse.ArgumentParser.parse_args",
                    return_value=argparse.Namespace(**kwargs),
                ),
            ):
                t_ret = _process_args()
                self.assertIsInstance(t_ret, tuple)
                files, is_fail_fast = t_ret
                self.assertIsInstance(files, tuple)
                files_count = len(files)
                self.assertEqual(files_count, file_count_expected)
                self.assertIsInstance(is_fail_fast, bool)
                self.assertTrue(is_fail_fast)

        # Success -- explict optional kwargs
        with (
            patch(
                "argparse.ArgumentParser.parse_args",
                return_value=argparse.Namespace(
                    **{
                        "dir": self.path_package_src,
                        "package": self.package,
                        "package_data_folder_start": self.package_data_folder_start,
                        "category": LoggingConfigCategory.WORKER.value,
                        "genre": "mp",
                        "flavor": "asz",
                        "version": "1",
                        "fail_fast": False,
                    },
                ),
            ),
        ):
            t_ret = _process_args()
            self.assertIsInstance(t_ret, tuple)
            files, is_fail_fast = t_ret
            self.assertIsInstance(files, tuple)
            files_count = len(files)
            self.assertEqual(files_count, 1)
            self.assertIsInstance(is_fail_fast, bool)
            self.assertFalse(is_fail_fast)

    def test_thru_api(self):
        """Call main directly rather than thru a subprocess"""
        yaml_snippet0 = "version: 1\n"
        yaml_snippet1 = "b: 'tuna fish'\n"
        try_these = (
            (yaml_snippet0, False, "Success / fail: 1 / 0"),
            (yaml_snippet0, True, "Success / fail: 1 / 0"),
            (yaml_snippet1, True, "Success / fail: 0 / 1"),
            (yaml_snippet1, False, "Success / fail: 0 / 1"),
        )
        for snippet, is_fail_fast, expected_ratio in try_these:
            with (tempfile.TemporaryDirectory() as fp,):
                path_dir = Path(fp)
                path_yaml = path_dir.joinpath(
                    f"mp.asz.worker{YAML_LOGGING_CONFIG_SUFFIX}"
                )
                path_yaml.touch(mode=0o644)
                path_yaml.write_text(snippet)
                with (
                    patch(
                        f"{g_app_name}.ep_validate_yaml._process_args",
                        return_value=((path_yaml,), is_fail_fast),
                    ),
                    redirect_stderr(io.StringIO()) as err,
                ):
                    main()
                actual = err.getvalue()
                self.assertIsInstance(actual, str)
                self.assertIn(expected_ratio, actual)


if __name__ == "__main__":  # pragma: no cover
    """Without coverage

    .. code-block:: shell

       python -m tests.test_ep --locals

       python -m unittest tests.test_ep \
       -k EntrypointStrictYAMLValidate.test_process_args --locals --verbose

       python -m unittest tests.test_ep \
       -k EntrypointStrictYAMLValidate.test_thru_api --locals --verbose


    With coverage

    .. code-block: shell

       coverage run --data-file=".coverage-combine-44" \
       -m unittest discover -t. -s tests -p "test_ep*.py" \
       --locals

       coverage report --include="**/ep_validate_yaml*" --no-skip-covered \
       --data-file=".coverage-combine-44"

    """
    unittest.main(tb_locals=True)
