"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

Module util_root assumes package or script can be run with root privledges.
Which is not a good idea.

For this test module, basic logging is setup.

"""

import logging
import os
import sys
import tempfile
import unittest
from pathlib import (
    Path,
    PurePath,
)
from unittest.mock import patch

from logging_strict.constants import g_app_name
from logging_strict.tech_niques import LoggerRedirector
from logging_strict.util.util_root import (
    IsRoot,
    check_python_not_old,
)

_LOGGER = logging.getLogger(f"{g_app_name}.tests.test_util_root")

# %(asctime)s
logging.basicConfig(
    format="%(levelname)s %(module)s: %(message)s",
    level=logging.INFO,
    stream=sys.stdout,
)


class UtilRoot(unittest.TestCase):
    """Module util_root tests"""

    def setUp(self) -> None:
        """On setup, redirect sys.stdout and sys.stderr"""
        LoggerRedirector.redirect_loggers(
            fake_stdout=sys.stdout, fake_stderr=sys.stderr
        )

    def tearDown(self) -> None:
        """On tear down, revert redirect of sys.stdout and sys.stderr."""
        LoggerRedirector.reset_loggers(
            fake_stdout=sys.stdout,
            fake_stderr=sys.stderr,
        )

    def test_path_home_root(self) -> None:
        """Test IsRoot.path_home_root"""
        path_home_root = IsRoot.path_home_root()

        # _LOGGER.info(f"path_home_root: {type(path_home_root)}")
        self.assertTrue(issubclass(type(path_home_root), PurePath))
        self.assertIsInstance(path_home_root, os.PathLike)

    # @unittest.skipUnless(os.geteuid() == 0, "Triggers callback when root")
    def test_set_owner_as_user(self) -> None:
        """Pretend a file is owned by root. And defang

        Normally act upon files that are owned by root, not user.
        To test will require to defang IsRoot.set_owner_as_user"""

        with (
            tempfile.NamedTemporaryFile(
                mode="w+",
                delete=True,
                prefix=g_app_name,
                suffix=".delete",
                encoding="utf8",
            ) as fp,
            patch(f"{g_app_name}.util.util_root.g_is_root", True),
            patch(
                f"{g_app_name}.util.util_root.get_logname",
                return_value="faulkmore",
            ),
            patch(
                f"{g_app_name}.util.util_root.getpwnam",
                return_value=("faulkmore", None, 1000, 1000),
            ),
            patch("shutil.chown", return_value=None),
        ):
            IsRoot.set_owner_as_user(
                fp.name,
                is_as_user=True,
            )

        """
        file_path = f"/root/{g_app_name}.deleteme"
        path_file = Path("/root").joinpath(f"{g_app_name}.deleteme")
        paths = (
            path_file,
            file_path,
        )
        for mixed_path in paths:
            if mixed_path.exists():
                mixed_path.unlink()
            self.assertFalse(mixed_path.exists())
            mixed_path.touch(
                mode=0o664,
                exist_ok=True,
            )
            IsRoot.set_owner_as_user(
                mixed_path,
                is_as_user=True,
            )
            # assert file owner user:user, rather than root:root
            self.assertEqual(mixed_path.owner(), os.getlogin())
            self.assertEqual(mixed_path.group(), os.getlogin())
            if mixed_path.exists():
                mixed_path.unlink()
        """
        pass


@patch(f"{g_app_name}.util.util_root.g_is_root", False)
@patch(f"{g_app_name}.util.util_root.ungraceful_app_exit", lambda: None)
class AsUser(unittest.TestCase):
    """Run tests with user privledges. Not root privledges."""

    def setUp(self) -> None:
        """On setup, redirect sys.stdout and sys.stderr"""
        LoggerRedirector.redirect_loggers(
            fake_stdout=sys.stdout, fake_stderr=sys.stderr
        )

    def tearDown(self) -> None:
        """On tear down, revert redirect of sys.stdout and sys.stderr."""
        LoggerRedirector.reset_loggers(
            fake_stdout=sys.stdout,
            fake_stderr=sys.stderr,
        )

    def test_set_owner_as_user(self) -> None:
        """No root privledge, so won't do nothing"""
        _LOGGER2 = logging.getLogger(f"{g_app_name}.sdafsadfsadfsdf")
        file_path = f"/tmp/{g_app_name}.deletemeasdfdsaf"
        path_file = Path("/tmp").joinpath(f"{g_app_name}.deletemeasdfdsaf")
        path_existing = Path("/proc").joinpath("version")
        paths = (
            path_file,  # not exists
            file_path,  # not exists
            0.12345,  # unsupported type
            _LOGGER2,  # unsupported type
            Path("/root"),  # not file
            path_existing,  # existing file
        )
        as_user = (
            None,
            False,
            True,
            _LOGGER2,  # unsupported type
        )
        for mixed_path in paths:
            for test_as_user in as_user:
                IsRoot.set_owner_as_user(
                    mixed_path,
                    is_as_user=test_as_user,
                )
        del _LOGGER2

    def test_assert_root(self) -> None:
        """Test IsRoot.is_root"""
        self.assertFalse(IsRoot.is_root())
        # Neither raise nor exit, therefore does nothing
        _LOGGER2 = logging.getLogger(f"{g_app_name}.sdafsadfsadfsdf")
        unsupported = (
            None,
            0.12345,
            _LOGGER2,
        )
        for no_support in unsupported:
            IsRoot.check_root(
                callback=None,
                is_app_exit=no_support,
                is_raise_exc=no_support,
            )
        del _LOGGER2
        # With callback
        cb = lambda msg_warn: self.assertTrue(len(msg_warn) != 0)  # noqa: E731
        with self.assertRaises(PermissionError):
            IsRoot.check_root(
                callback=cb,
                is_app_exit=False,
                is_raise_exc=True,
            )


@patch(f"{g_app_name}.util.util_root.g_is_root", True)
@patch(f"{g_app_name}.util.util_root.ungraceful_app_exit", lambda: None)
class AsRoot(unittest.TestCase):
    """Run tests as fake root privledges. Not user level privledges."""

    def setUp(self) -> None:
        """On setup, redirect sys.stdout and sys.stderr"""
        LoggerRedirector.redirect_loggers(
            fake_stdout=sys.stdout, fake_stderr=sys.stderr
        )

    def tearDown(self) -> None:
        """On tear down, revert redirect of sys.stdout and sys.stderr."""
        LoggerRedirector.reset_loggers(
            fake_stdout=sys.stdout,
            fake_stderr=sys.stderr,
        )

    def test_assert_not_root(self):
        """Test IsRoot.check_not_root"""
        is_app_exits = (
            None,
            False,
            True,
            0.12345,
        )
        is_raise_excs = (
            None,
            False,
            0.12345,
        )
        # Practice exiting app, if root
        for is_app_exit in is_app_exits:
            IsRoot.check_not_root(is_app_exit=is_app_exit)

        # Practice (not) raise exception, if root
        for is_raise_exc in is_raise_excs:
            IsRoot.check_not_root(is_raise_exc=is_raise_exc)

        # Practice raise exception, if root
        with self.assertRaises(PermissionError):
            IsRoot.check_not_root(is_raise_exc=True)

        # Callback -- normally prints or logs msg
        # With callback
        cb = lambda msg_warn: self.assertTrue(len(msg_warn) != 0)  # noqa: E731
        IsRoot.check_not_root(callback=cb)

    def test_check_root(self) -> None:
        """Just covers parameter checking"""
        is_app_exits = (
            None,
            False,
            True,
            0.12345,
        )
        is_raise_excs = (
            None,
            False,
            0.12345,
        )
        # Practice exiting app, if root
        for is_app_exit in is_app_exits:
            IsRoot.check_root(is_app_exit=is_app_exit)

        # Practice (not) raise exception, if root
        for is_raise_exc in is_raise_excs:
            IsRoot.check_root(is_raise_exc=is_raise_exc)


@patch(f"{g_app_name}.util.util_root.is_python_old", True)
@patch(f"{g_app_name}.util.util_root.ungraceful_app_exit", lambda: None)
class UnsupportedPython(unittest.TestCase):
    """Test check for detecting usage old python interpretor."""

    def setUp(self) -> None:
        """On setup, redirect sys.stdout and sys.stderr"""
        LoggerRedirector.redirect_loggers(
            fake_stdout=sys.stdout, fake_stderr=sys.stderr
        )

    def tearDown(self) -> None:
        """On tear down, revert redirect of sys.stdout and sys.stderr."""
        LoggerRedirector.reset_loggers(
            fake_stdout=sys.stdout,
            fake_stderr=sys.stderr,
        )

    def test_check_python_not_old(self) -> None:
        """Test check_python_not_old"""
        _LOGGER2 = logging.getLogger(f"{g_app_name}.sdafsadfsadfsdf")
        unsupported = (
            None,
            0.12345,
            _LOGGER2,
        )
        for no_support in unsupported:
            check_python_not_old(
                callback=None,
                is_app_exit=no_support,
                is_raise_exc=no_support,
            )
        del _LOGGER2
        # With callback
        cb = lambda msg_warn: self.assertTrue(len(msg_warn) != 0)  # noqa: E731
        with self.assertRaises(PermissionError):
            check_python_not_old(
                callback=cb,
                is_app_exit=False,
                is_raise_exc=True,
            )

        # app exit
        check_python_not_old(
            callback=None,
            is_app_exit=True,
            is_raise_exc=False,
        )


@patch(f"{g_app_name}.util.util_root.is_python_old", False)
@patch(f"{g_app_name}.util.util_root.ungraceful_app_exit", lambda: None)
class SupportedPython(unittest.TestCase):
    """Test check showing current python interpretor is still supported version."""

    def setUp(self) -> None:
        """On setup, redirect sys.stdout and sys.stderr"""
        LoggerRedirector.redirect_loggers(
            fake_stdout=sys.stdout, fake_stderr=sys.stderr
        )

    def tearDown(self) -> None:
        """On tear down, revert redirect of sys.stdout and sys.stderr."""
        LoggerRedirector.reset_loggers(
            fake_stdout=sys.stdout,
            fake_stderr=sys.stderr,
        )

    def test_check_python_not_old(self) -> None:
        """Test check_python_not_old"""
        _LOGGER2 = logging.getLogger(f"{g_app_name}.sdafsadfsadfsdf")
        unsupported = (
            None,
            0.12345,
            _LOGGER2,
        )
        for no_support in unsupported:
            check_python_not_old(
                callback=None,
                is_app_exit=no_support,
                is_raise_exc=no_support,
            )
        del _LOGGER2
        # With callback. Never called
        cb = lambda msg_warn: self.assertTrue(len(msg_warn) != 0)  # noqa: E731
        check_python_not_old(
            callback=cb,
            is_app_exit=False,
            is_raise_exc=True,
        )

        # app exit
        check_python_not_old(
            callback=None,
            is_app_exit=True,
            is_raise_exc=False,
        )


if __name__ == "__main__":  # pragma: no cover
    """Without coverage

    .. code-block:: shell

       python -m tests.test_util_root --locals


    With coverage

    .. code-block:: shell

       coverage run --data-file=".coverage-combine-1" -m unittest discover \
       -t. -s tests -p "test_util_root*.py" --local

       coverage report --data-file=".coverage-combine-1" --no-skip-covered \
       --include="**/util/util_root*"

    """
    unittest.main(tb_locals=True)
