"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

Gaining access to use standard folders. The user standard folders are
useful. The system standard folders would require write permissions.
Normally only have read access to system folders.

These standard folders are normally on-disk, not in-memory.
Important to have an option to override to instead specify a temp folder.

"""

import platform
import unittest
from pathlib import Path

from logging_strict.util.xdg_folder import (
    DestFolderSite,
    DestFolderUser,
    _get_author,
    _get_path_config,
)


class XdgFolders(unittest.TestCase):
    """Platform mostly independent standard folders"""

    def test_get_author(self):
        """Honour dependency authors"""
        commas = "Guido-van-Rossum-Jukka-Lehtosalo-Łukasz-Langa-Michael-Lee"
        single_quote = "Colm-OConnor"
        dependencies = (
            ("appdirs", True, True, True, "Trent-Mick"),
            ("attrs", False, False, False, "Hynek Schlawack"),
            ("python_dateutil", False, True, False, "Gustavo-Niemeyer"),
            ("six", False, True, False, "Benjamin-Peterson"),
            ("strictyaml", False, True, False, single_quote),
            ("typing_extensions", False, True, False, commas),
        )
        for pkg, no_period, no_space, no_underscore, expected in dependencies:
            actual = _get_author(
                pkg,
                no_period=no_period,
                no_space=no_space,
                no_underscore=no_underscore,
            )
            self.assertEqual(actual, expected)

    @unittest.skipUnless(platform.system() == "Linux", "Results for Linux")
    def test_dest_folder_site(self):
        """Would require an installer that is run with root privledges"""
        # multipath False
        valids = (
            (
                "appdirs",
                True,
                True,
                True,
                None,
                False,
                "data_dir",
                "/usr/local/share/appdirs",
            ),
            (
                "appdirs",
                True,
                True,
                True,
                None,
                False,
                "config_dir",
                "/etc/xdg/appdirs",
            ),
        )
        for (
            pkg,
            no_period,
            no_space,
            no_underline,
            with_version,
            multipath,
            prop_name,
            expected,
        ) in valids:
            inst = DestFolderSite(
                pkg,
                author_no_period=no_period,
                author_no_space=no_space,
                author_no_underscore=no_underline,
                version=with_version,
                multipath=multipath,
            )
            actual = getattr(inst, prop_name)
            self.assertEqual(actual, expected)

        # multipath True
        valids = (
            (
                "appdirs",
                True,
                True,
                True,
                None,
                True,
                "data_dir",
                "/usr/local/share/appdirs:/usr/share/appdirs",
            ),
            (
                "appdirs",
                True,
                True,
                True,
                None,
                False,
                "config_dir",
                "/etc/xdg/appdirs",
            ),
        )
        for (
            pkg,
            no_period,
            no_space,
            no_underline,
            with_version,
            multipath,
            prop_name,
            expected,
        ) in valids:
            inst = DestFolderSite(
                pkg,
                author_no_period=no_period,
                author_no_space=no_space,
                author_no_underscore=no_underline,
                version=with_version,
                multipath=multipath,
            )
            actual = getattr(inst, prop_name)
            self.assertTrue(actual.startswith(expected))

    @unittest.skipUnless(platform.system() == "Linux", "Results for Linux")
    def test_dest_folder_user(self):
        """User dest folder is more appropriate for python packages"""
        # roaming is a Windows thing
        # opinion requires effort to track down when it applies
        valids = (
            (
                "appdirs",
                True,
                True,
                True,
                None,
                False,
                True,
                "data_dir",
                f"{str(Path.home())}/.local/share/appdirs",
            ),
            (
                "appdirs",
                True,
                True,
                True,
                None,
                False,
                True,
                "config_dir",
                f"{str(Path.home())}/.config/appdirs",
            ),
            (
                "appdirs",
                True,
                True,
                True,
                None,
                False,
                True,
                "cache_dir",
                f"{str(Path.home())}/.cache/appdirs",
            ),
            (
                "appdirs",
                True,
                True,
                True,
                None,
                False,
                True,
                "log_dir",
                f"{str(Path.home())}/.cache/appdirs/log",
            ),
            (
                "appdirs",
                True,
                True,
                True,
                None,
                False,
                True,
                "state_dir",
                f"{str(Path.home())}/.local/state/appdirs",
            ),
        )
        for (
            pkg,
            no_period,
            no_space,
            no_underline,
            with_version,
            roaming,
            opinion,
            prop_name,
            expected,
        ) in valids:
            inst = DestFolderUser(
                pkg,
                author_no_period=no_period,
                author_no_space=no_space,
                author_no_underscore=no_underline,
                version=with_version,
                roaming=roaming,
                opinion=opinion,
            )
            actual = getattr(inst, prop_name)
            self.assertEqual(actual, expected)

    @unittest.skipUnless(platform.system() == "Linux", "Results for Linux")
    def test_get_path_config(self):
        """Same as user data dir"""
        valids = (
            (
                "appdirs",
                True,
                True,
                True,
                None,
                False,
                Path.home().joinpath(".local", "share", "appdirs"),
            ),
        )
        for (
            pkg,
            no_period,
            no_space,
            no_underline,
            with_version,
            roaming,
            expected,
        ) in valids:
            path_actual = _get_path_config(
                pkg,
                author_no_period=no_period,
                author_no_space=no_space,
                author_no_underscore=no_underline,
                version=with_version,
                roaming=roaming,
            )
            self.assertEqual(path_actual, expected)


if __name__ == "__main__":  # pragma: no cover
    """Without coverage

    .. code-block:: shell

       python -m tests.test_xdg_folders --locals

    .. code-block:: shell

       coverage run --data-file=".coverage-combine-2" \
       -m unittest discover -t. -s tests -p "test_xdg_folder*.py" --locals

       coverage report --include="**/util/*xdg_folder*" --no-skip-covered \
       --data-file=".coverage-combine-2"

       coverage report --data-file=".coverage-combine-2" --no-skip-covered

    """
    unittest.main(tb_locals=True)
