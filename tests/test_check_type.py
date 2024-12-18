"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

Unittest for check_type module

"""

import platform
import tempfile
import unittest
from pathlib import (
    Path,
    PurePath,
)
from typing import Optional
from unittest.mock import patch

from logging_strict.util.check_type import (
    check_int_verbosity,
    check_start_folder_importable,
    check_type_path,
    is_not_ok,
    is_ok,
)


class CommonChecks(unittest.TestCase):
    """Check types tests"""

    def setUp(self):
        """Initialize settings: base folder and package base folder."""
        if "__pycache__" in __file__:
            # cached
            self.path_tests = Path(__file__).parent.parent
        else:
            # not cached
            self.path_tests = Path(__file__).parent
        self.path_cwd = self.path_tests.parent

    def test_is_ok(self):
        """Is not None, a str, and not just whitespace, non-empty string"""
        invalids = (
            None,  # not str
            "",  # empty string
            0.123,  # not str
            "    ",  # contains only whitespace
        )
        for invalid in invalids:
            out_actual = is_ok(invalid)
            self.assertFalse(out_actual)

        valids = ("Hello World!",)  # non-empty string
        for valid in valids:
            out_actual = is_ok(valid)
            self.assertTrue(out_actual)

    def test_is_not_ok(self):
        """Not ok opposite of is_ok. None, contains just whitespace, or not a str"""
        invalids = ("Hello World!",)
        for invalid in invalids:
            out_actual = is_not_ok(invalid)
            self.assertFalse(out_actual)

        valids = (
            None,
            "",
            "    ",
            0.1234,
        )
        for valid in valids:
            out_actual = is_not_ok(valid)
            self.assertTrue(out_actual)

    def test_check_type_path(self):
        """Check for pathlib.Path and os.PathLike"""
        path_unittests_dir = self.path_tests
        path_cwd = self.path_cwd

        path_attrs = (
            ("path_unittest_dir", path_unittests_dir),
            ("path_cwd", path_cwd),
        )

        # RuntimeError -- simulating no home folder **or** invalid path
        for attr_name, attr_val in path_attrs:
            with patch("pathlib.Path.expanduser", side_effect=RuntimeError):
                with self.assertRaises(ValueError):
                    check_type_path(attr_val)

        for attr_name, attr_val in path_attrs:
            # pathlib.Path
            out = check_type_path(attr_val)
            self.assertTrue(out)
            # str
            out = check_type_path(str(attr_val))
            self.assertTrue(out)

        # unsupported type
        invalids = (
            None,
            0.1234,
        )
        for invalid in invalids:
            with self.assertRaises(TypeError):
                check_type_path(invalid)

        # non-empty str and Exception raised
        module_path = "this won't end well"
        with patch("pathlib.Path.expanduser", side_effect=RuntimeError):
            with self.assertRaises(ValueError):
                check_type_path(module_path)


class RarelyUsedChecks(unittest.TestCase):
    """More specialized checks. Possibly specific to package logging-strict"""

    def test_check_int_verbosity(self):
        """Test function check_int_verbosity"""
        # None
        invalids = (
            None,  # None
            ("hello world",),  # other type
            11,  # not in [1, 2]
        )
        for invalid in invalids:
            out = check_int_verbosity(invalid)
            self.assertIsInstance(out, bool)
            self.assertFalse(out)

        # int valid
        valids = (
            1,
            2,
        )
        for valid in valids:
            out = check_int_verbosity(valid)
            self.assertIsInstance(out, bool)
            self.assertTrue(out)

    def test_check_start_folder_importable(self):
        """Test function check_start_folder_importable"""
        # unsupported type
        with self.assertRaises(TypeError):
            check_start_folder_importable(4)

        # relative folder
        target_relative = Path("")
        self.assertFalse(check_start_folder_importable(target_relative))

        # relative file unsupported. Not a folder
        with self.assertRaises(NotADirectoryError):
            target_relative = "__init__.py"
            self.assertFalse(check_start_folder_importable(target_relative))

        # In actual folder, __init__.py not found within folder. Not a package
        if platform.system().lower() != "windows":
            path_folder_not_package = Path("/etc")
            self.assertFalse(check_start_folder_importable(path_folder_not_package))

        # Insane person created a folder or symlink named, __init__.py
        class TempFolder:
            """Roll your own temp folder context manager"""

            def __init__(self, folder_base, folder_name) -> None:
                """Class constructor"""
                self.target_name = folder_name

                path_folder_tmp = Path(folder_base)
                self.path_target = path_folder_tmp.joinpath(self.target_name)

            def __enter__(self):
                """Enter context manager"""
                if not self.path_target.exists():
                    self.path_target.mkdir(
                        mode=0o700,
                        parents=False,
                        exist_ok=False,
                    )
                    ret = self.path_target
                elif self.path_target.exists() and self.path_target.is_dir():
                    ret = self.path_target
                else:
                    ret = None

                return ret

            def __exit__(self, exc_type, exc_value, tb):
                """Exit context manager. Do whatever cleanup is required."""
                pass

        # Folder contains a __init__.py file
        class TempFile:
            """Roll your own Temp file context manager."""

            def __init__(self, tmp_folder, file_name) -> None:
                """Class constructor"""
                self.path_target = Path(tmp_folder).joinpath(file_name)

            def __enter__(self) -> Optional[Path]:
                """Enter context manager"""
                if not self.path_target.exists():
                    self.path_target.touch(mode=0o600, exist_ok=True)
                    return self.path_target
                elif self.path_target.exists() and not self.path_target.is_file():
                    return None
                else:
                    return self.path_target

            def __exit__(self, exc_type, exc_value, tb) -> None:
                """Exit context manager. Do whatever cleanup is required."""
                if self.path_target.exists() and self.path_target.is_file():
                    self.path_target.unlink()

        with tempfile.TemporaryDirectory() as tmp_dir_path:
            # temp file must be unlink'ed
            with TempFile(tmp_dir_path, "__init__.py"):
                self.assertTrue(
                    check_start_folder_importable(tmp_dir_path),
                )

            with TempFolder(tmp_dir_path, "__init__.py") as path_dir:
                self.assertIsNotNone(path_dir)
                self.assertTrue(issubclass(type(path_dir), PurePath))
                self.assertTrue(path_dir.exists() and path_dir.is_dir())
                self.assertFalse(check_start_folder_importable(tmp_dir_path))


if __name__ == "__main__":  # pragma: no cover
    """Without coverage

    .. code-block:: shell

       python -m tests.test_check_type

    With coverage

    .. code-block:: shell

       coverage run --data-file=".coverage-combine-11" -m unittest discover \
       -t. -s tests -p "test_check_type*.py" --local

       coverage report --data-file=".coverage-combine-11" --no-skip-covered \
       --include="*check_type*"

    """
    unittest.main(tb_locals=True)
