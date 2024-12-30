"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

Extracting package data module

Extract package resources. Can extract many, not just one at a time.

"""

import logging
import os
import platform
import secrets
import sys
import tempfile
import unittest
from contextlib import suppress
from functools import partial
from pathlib import (
    Path,
    PurePath,
)
from unittest.mock import patch

from logging_strict.constants import g_app_name
from logging_strict.tech_niques import (
    LoggerRedirector,
    captureLogs,
)
from logging_strict.util.package_resource import (  # noqa: F401 sphinx uses
    PackageResource,
    _extract_folder,
    _get_package_data_folder,
    _to_package_case,
    filter_by_file_stem,
    filter_by_suffix,
    is_package_exists,
    msg_stem,
    walk_tree_folders,
)

if sys.version_info >= (3, 9):  # pragma: no cover
    from collections.abc import Generator
else:  # pragma: no cover
    from typing import Generator

g_module = f"{g_app_name}.tests.test_util_package_resource"


class PackageResourceMadness(unittest.TestCase):
    """Class containing tests covering package resource extraction."""

    def setUp(self) -> None:
        """Setup syncronous logging redirection and logging."""
        self.package_dest_c = g_app_name
        self.fallback_package_base_folder = "configs"

        # unittest has reassigned sys.stdout and sys.stderr by this point
        # %(asctime)s
        logging.basicConfig(
            format="%(levelname)s %(module)s: %(message)s",
            level=logging.NOTSET,
        )
        # define a Handler which writes INFO messages or higher to the sys.stderr
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        # set a format which is simpler for console use
        formatter = logging.Formatter("%(name)-12s: %(levelname)-8s %(message)s")
        # tell the handler to use this format
        console.setFormatter(formatter)
        # add the handler to the root logger
        logging.getLogger("").addHandler(console)

        self._LOGGER = logging.getLogger(g_module)

        LoggerRedirector.redirect_loggers(
            fake_stdout=sys.stdout,
            fake_stderr=sys.stderr,
        )
        # logging.info(f"g_module: {g_module}")
        pass

    def tearDown(self) -> None:
        """unittest will revert sys.stdout and sys.stderr after this"""
        LoggerRedirector.reset_loggers(
            fake_stdout=sys.stdout,
            fake_stderr=sys.stderr,
        )

    def test_get_parent_paths(self) -> None:
        """PartSuffix and PartStem are for type checking.

        Not needed in a unit test, but would normally also be imported and
        used to indicate type of cb_file_stem and cb_file_suffix
        """
        # Default folder :menuselection:`data --> config`
        pr = PackageResource(self.package_dest_c, self.fallback_package_base_folder)
        pr2 = PackageResource(self.package_dest_c, "bad_idea")

        # Positive results -- Two files found, only one in correct folder
        file_name = "mp_1_shared.worker.logging.config.yaml"
        cb_file_stem = partial(
            filter_by_file_stem,
            "mp_1_shared",
        )
        cb_file_suffix = partial(
            filter_by_suffix,
            ".worker.logging.config.yaml",
        )
        # start dir is last folder. No parent folders. Needs to widen search
        d_relative = pr2.get_parent_paths(
            cb_suffix=cb_file_suffix,
            cb_file_stem=cb_file_stem,
            path_relative_package_dir="folder0",
            parent_count=1,
        )
        self.assertIsInstance(d_relative, dict)
        key_count = len(d_relative.keys())
        self.assertEqual(key_count, 1)
        seq_result = d_relative[file_name]
        self.assertEqual(len(seq_result), 0)

        """Two file match. From start folder, parent folders:

        .. code-block:: text

           d_relative = {
               'folder1/mp_1_shared.worker.logging.config.yaml': ('folder1',),
               'folder0/mp_1_shared.worker.logging.config.yaml': ('folder0',),
           }

        key is relative path from start folder
        value is the relative (to start dir) parents (of package data file)
        """
        d_relative = pr2.get_parent_paths(
            cb_suffix=cb_file_suffix,
            cb_file_stem=cb_file_stem,
            path_relative_package_dir="bad_idea",
            parent_count=1,
        )
        self.assertIsInstance(d_relative, dict)
        key_count = len(d_relative.keys())
        self.assertEqual(key_count, 2)
        for key, val in d_relative.items():
            path_left = str(Path(key).parent)  # strips file name
            path_right = Path(*val)  # combines relative parent folders
            self.assertEqual(str(path_left), str(path_right))

        # Switch search query
        file_name = "textual_1_asz.app.logging.config.yaml"
        cb_file_stem = partial(
            filter_by_file_stem,
            "textual_1_asz",
        )
        cb_file_suffix = partial(
            filter_by_suffix,
            ".app.logging.config.yaml",
        )

        # Files exist, but nonexistent folder. Empty resultset
        paths = (
            "$~..!#%(|=-_*+-[&)/curre]n>c<y",
            Path("$~..!#%(|=-_*+-[&)/curre]n>c<y"),
        )
        for mixed_path in paths:
            d_relative = pr.get_parent_paths(
                cb_suffix=cb_file_suffix,
                cb_file_stem=cb_file_stem,
                path_relative_package_dir=mixed_path,
                parent_count=1,
            )
            self.assertIsInstance(d_relative, dict)
            key_count = len(d_relative.keys())
            self.assertEqual(key_count, 0)

        """None | unsupported type --> fallback folder "configs".
        NOT THE PACKAGE BASE FOLDER

        Expected. file name and there are no
        (relative to config folder) parent folders
        """
        d_expected = {file_name: ()}
        _LOGGER2 = logging.getLogger(f"{g_app_name}.sdafsadfsadfsdf")

        paths = (
            None,
            _LOGGER2,
            0.12345,
            pr.package_data_folder_start,
        )
        for mixed_path in paths:
            d_relative = pr.get_parent_paths(
                cb_suffix=cb_file_suffix,
                cb_file_stem=cb_file_stem,
                path_relative_package_dir=mixed_path,
                parent_count=1,
            )
            self.assertIsInstance(d_relative, dict)
            for key, val in d_relative.items():
                self.assertTrue(key in d_expected.keys())
                self.assertIsInstance(val, tuple)
                self.assertEqual(len(val), 0)  # there are no relative parent dirs

        del _LOGGER2

        # cb_suffix and cb_file_stem are required. Empty resultset
        # Should this be ValueError ??
        d_relative = pr.get_parent_paths(
            cb_suffix=None,
            cb_file_stem=None,
        )
        self.assertIsInstance(d_relative, dict)
        self.assertTrue(len(d_relative.keys()) == 0)

        # parent_count = 0 --> No parents of relative path
        d_relative = pr.get_parent_paths(
            cb_suffix=cb_file_suffix,
            cb_file_stem=cb_file_stem,
            path_relative_package_dir=pr.package_data_folder_start,
            parent_count=0,
        )
        for key, val in d_relative.items():
            self.assertEqual(key, file_name)
            self.assertIsInstance(val, tuple)
            self.assertEqual(len(val), 0)

        # not_a_parent -- No such package data folder. Empty resultset
        d_relative = pr.get_parent_paths(
            cb_suffix=cb_file_suffix,
            cb_file_stem=cb_file_stem,
            path_relative_package_dir="not_a_parent",
            parent_count=1,
        )
        self.assertIsInstance(d_relative, dict)
        self.assertTrue(len(d_relative.keys()) == 0)

        # Within package, both do not exist: data file and folder. Empty resultset
        cb_file_stem = partial(
            filter_by_file_stem,
            "textual_1_asz",
        )
        cb_file_suffix = partial(
            filter_by_suffix,
            ".ini.yaml",  # obvious nonsense
        )
        d_relative = pr.get_parent_paths(
            cb_suffix=cb_file_suffix,
            cb_file_stem=cb_file_stem,
            path_relative_package_dir="not_a_parent",
            parent_count=1,
        )
        self.assertIsInstance(d_relative, dict)
        self.assertTrue(len(d_relative.keys()) == 0)

    def test_path_relative(self) -> None:
        """Test PackageResource.path_relative

        :py:func:`path_relative` is normally called by
        :py:func:`get_parent_paths`. Which processes unsuccessful
        lookups which causes Exceptions:

        - :py:exc:`TypeError`

        - :py:exc:`LookupError`

        Without :py:func:`get_parent_paths`, have to deal with both
        successful and unsuccessful lookups
        """

        """ Simulate package data extracted with
            :py:meth:`importlib_resources.as_file`. Which will be an
            absolute path including the package data folder "data"
        """
        pr = PackageResource(self.package_dest_c, self.fallback_package_base_folder)

        package_dest_c = self.package_dest_c
        package_specific_data_folder_fallback = self.fallback_package_base_folder

        path_local_cache = Path(_extract_folder(package_dest_c))
        path_json_bad = path_local_cache.joinpath(
            package_specific_data_folder_fallback,
            "currency",
            "nonsense",
            "digital_tox_default.ini",
        )

        # path_relative.y unsupported --> TypeError
        _LOGGER2 = logging.getLogger(f"{self.package_dest_c}.sdafsadfsadfsdf")
        paths = (
            None,
            _LOGGER2,
        )
        for mixed_path in paths:
            with self.assertRaises(TypeError):
                pr.path_relative(
                    mixed_path,
                    path_relative_package_dir=None,  # --> "configs"
                    parent_count=1,
                )

        # path_relative.path_relative_package_dir unsupported type
        #    full relative path with one parent (folder)
        paths = (path_json_bad,)
        for mixed_path in paths:
            path_out = pr.path_relative(
                mixed_path,
                path_relative_package_dir=_LOGGER2,  # --> "configs"
                parent_count=1,
            )
            if platform.system().lower() == "windows":
                expected_relpath = "nonsense\\digital_tox_default.ini"
            else:
                expected_relpath = "nonsense/digital_tox_default.ini"
            self.assertEqual(str(path_out), expected_relpath)
        del _LOGGER2

        # path_relative.path_relative_package_dir None --> "configs"
        paths = (path_json_bad,)
        #    Want 1 parent folders
        for mixed_path in paths:
            path_out = pr.path_relative(
                mixed_path,
                path_relative_package_dir=None,
                parent_count=1,
            )
            if platform.system().lower() == "windows":
                expected_relpath = "nonsense\\digital_tox_default.ini"
            else:
                expected_relpath = "nonsense/digital_tox_default.ini"
            self.assertEqual(str(path_out), expected_relpath)

        # Want 2 parent folders
        for mixed_path in paths:
            path_out = pr.path_relative(
                mixed_path,
                path_relative_package_dir=None,
                parent_count=2,
            )
            if platform.system().lower() == "windows":
                expected_relpath = "currency\\nonsense\\digital_tox_default.ini"
            else:
                expected_relpath = "currency/nonsense/digital_tox_default.ini"
            self.assertEqual(str(path_out), expected_relpath)

        # Want 3 parent folders, there is only two
        for mixed_path in paths:
            path_out = pr.path_relative(
                mixed_path,
                path_relative_package_dir=None,
                parent_count=3,
            )
            if platform.system().lower() == "windows":
                expected_relpath = "currency\\nonsense\\digital_tox_default.ini"
            else:
                expected_relpath = "currency/nonsense/digital_tox_default.ini"
            self.assertEqual(str(path_out), expected_relpath)

        # Want 3 parent folders, there is only two. parent_count means want all
        for mixed_path in paths:
            path_out = pr.path_relative(
                mixed_path,
                path_relative_package_dir=None,
                parent_count=None,
            )
            if platform.system().lower() == "windows":
                expected_relpath = "currency\\nonsense\\digital_tox_default.ini"
            else:
                expected_relpath = "currency/nonsense/digital_tox_default.ini"
            self.assertEqual(str(path_out), expected_relpath)

        # Want 0 parent folders
        for mixed_path in paths:
            path_out = pr.path_relative(
                mixed_path,
                path_relative_package_dir=None,
                parent_count=0,
            )
            self.assertEqual(str(path_out), "digital_tox_default.ini")

        # non-existing parent
        for mixed_path in paths:
            with self.assertRaises(LookupError):
                path_out = pr.path_relative(
                    mixed_path,
                    path_relative_package_dir="not-a-parent",
                    parent_count=0,
                )

    def test_filter_by_suffix(self) -> None:
        """Test filter_by_suffix function"""
        # None
        cb_file_suffix = partial(filter_by_suffix, None)
        self.assertFalse(cb_file_suffix(".txt"))
        self.assertFalse(cb_file_suffix((".txt", ".rst", ".md")))
        self.assertTrue(cb_file_suffix(""))
        self.assertTrue(cb_file_suffix(None))

        # tuple
        tuple_expected = (".txt", ".rst", ".md")
        cb_file_suffix = partial(filter_by_suffix, tuple_expected)
        self.assertTrue(cb_file_suffix(".txt"))
        self.assertTrue(cb_file_suffix(".rst"))
        self.assertTrue(cb_file_suffix(".md"))
        self.assertFalse(cb_file_suffix(""))
        self.assertFalse(cb_file_suffix(None))
        self.assertFalse(cb_file_suffix(".html"))

    def test_resource_extract(self) -> None:
        """Test PackageResource.resource_extract

        As opposed to cache_extract; changeable dest folder.

        Can also be called by an installer, to install package
        data resources to privledged locations, changing
        permissions and ownership as needed

        :py:mod:unittest runs unprivledged. Test the
        branches which run unprivledged
        """
        pr = PackageResource(self.package_dest_c, self.fallback_package_base_folder)
        pr2 = PackageResource(self.package_dest_c, "bad_idea")
        pr_bad = PackageResource(
            "zadfdzaf98769876dsfzdfdzfadz43f", self.fallback_package_base_folder
        )

        package_dest_c = self.package_dest_c
        cb_file_stem = partial(filter_by_file_stem, "mp_1_asz")
        cb_file_suffix = partial(filter_by_suffix, ".worker.logging.config.yaml")

        # str
        overwrites = (
            True,
            True,
            False,
            False,
        )
        with tempfile.TemporaryDirectory() as fp:
            for overwrite in overwrites:
                # Generator; no __enter__ __exit__ handlers
                generator_folder = pr.package_data_folders(
                    cb_suffix=cb_file_suffix,
                    cb_file_stem=cb_file_stem,
                )
                gen_paths = pr.resource_extract(
                    generator_folder,
                    fp,
                    cb_suffix=cb_file_suffix,
                    cb_file_stem=cb_file_stem,
                    is_overwrite=overwrite,
                    as_user=True,
                )
                self.assertIsInstance(gen_paths, Generator)
                paths = list(gen_paths)  # runs generator
                files_count = len(paths)
                self.assertEqual(files_count, 1)
                for path_f in paths:
                    self.assertTrue(issubclass(type(path_f), PurePath))
                    self.assertTrue(path_f.exists() and path_f.is_file())
                    # adulterize file, by changing file size
                    if overwrite:
                        str_text = path_f.read_text()
                        str_text = f"{str_text} safdsad fsadfdsaf sad f af fdssaf"
                        path_f.write_text(str_text)

        # path_dest unsupported type --> yield from ()
        paths = (
            0.12345,
            "",
            "     ",
            None,
        )
        for mixed_path in paths:
            gen_folder = pr.package_data_folders(
                cb_suffix=cb_file_suffix,
                cb_file_stem=cb_file_stem,
            )
            gen_paths = pr.resource_extract(
                gen_folder,
                mixed_path,
                cb_suffix=cb_file_suffix,
                cb_file_stem=cb_file_stem,
                is_overwrite=True,
                as_user=True,
            )
            self.assertIsInstance(gen_paths, Generator)
            paths = list(gen_paths)
            files_count = len(paths)
            self.assertEqual(files_count, 0)

        # unsupported type --> fallback --> local cache folder
        path_default = Path(_extract_folder(package_dest_c))

        paths = (
            path_default,
            str(path_default),
        )
        path_f_last = None
        for mixed_path in paths:
            generator_folder = pr.package_data_folders(
                cb_suffix=cb_file_suffix,
                cb_file_stem=cb_file_stem,
            )
            for path_f in pr.resource_extract(
                generator_folder,
                mixed_path,
                cb_suffix=cb_file_suffix,
                cb_file_stem=cb_file_stem,
                is_overwrite=True,
                as_user=True,
            ):
                self.assertTrue(issubclass(type(path_f), PurePath))
                self.assertTrue(path_f.exists() and path_f.is_file())
                self.assertTrue(path_f.parent, path_default)
                path_f_last = path_f
        with suppress(Exception):
            if (
                path_f_last is not None
                and path_f_last.exists()
                and path_f_last.is_file()
            ):
                path_f_last.unlink()

        # generator_folder created with non-existing package
        path_f_last = None
        for mixed_path in paths:
            generator_folder = pr_bad.package_data_folders(
                cb_suffix=cb_file_suffix,
                cb_file_stem=cb_file_stem,
            )
            # Both traceback (INFO) and WARNING logged
            with captureLogs("", level="INFO"):
                for path_f in pr_bad.resource_extract(
                    generator_folder,
                    mixed_path,
                    cb_suffix=cb_file_suffix,
                    cb_file_stem=cb_file_stem,
                    is_overwrite=True,
                    as_user=True,
                ):
                    # Never executed
                    self.assertTrue(False)
                else:
                    # No paths cuz empty generator
                    self.assertTrue(True)

        query_start_dir = "folder0"
        cb_file_stem = partial(filter_by_file_stem, "mp_1_shared")
        cb_file_suffix = partial(filter_by_suffix, ".worker.logging.config.yaml")
        with tempfile.TemporaryDirectory() as fp:
            for mixed_path in paths:
                gen_folder = pr2.package_data_folders(
                    cb_suffix=cb_file_suffix,
                    cb_file_stem=cb_file_stem,
                    path_relative_package_dir=query_start_dir,
                )
                folders = list(gen_folder)  # Run generator
                folder_count = len(folders)
                self.assertEqual(folder_count, 2)

                # Refresh generator
                gen_folder = pr2.package_data_folders(
                    cb_suffix=cb_file_suffix,
                    cb_file_stem=cb_file_stem,
                    path_relative_package_dir=query_start_dir,
                )
                gen_paths = pr2.resource_extract(
                    gen_folder,
                    fp,
                    cb_suffix=cb_file_suffix,
                    cb_file_stem=cb_file_stem,
                    is_overwrite=True,
                    as_user=True,
                )
                self.assertIsInstance(gen_paths, Generator)
                paths = list(gen_paths)  # Run generator
                files_count = len(paths)
                self.assertEqual(files_count, 2)

    @unittest.skipUnless(platform.system() == "Linux", "requires Linux")
    def test_resource_extract_nonexistent_folder(self) -> None:
        """Allow resource_extract to mkdir"""
        pr = PackageResource(self.package_dest_c, self.fallback_package_base_folder)

        # Not previously existing folder
        euid = os.geteuid()
        folder_name = secrets.token_urlsafe()
        path_dest_base = Path("/run").joinpath("user", str(euid))
        path_dest = path_dest_base.joinpath(folder_name)

        self.assertTrue(path_dest_base.exists() and path_dest_base.is_dir())

        # If necessary, try to :py:func:`Path.rmdir`
        if path_dest.exists() and path_dest.is_dir():
            with suppress(Exception):
                path_dest.rmdir()
        self.assertFalse(path_dest.exists() or path_dest.is_dir())

        cb_file_stem = partial(filter_by_file_stem, "mp_1_asz")
        cb_file_suffix = partial(filter_by_suffix, ".worker.logging.config.yaml")

        path_last_f = None
        # 2nd iteration, so have a chance to overwrite existing file
        for num in range(0, 2):
            generator_folder = pr.package_data_folders(
                cb_suffix=cb_file_suffix,
                cb_file_stem=cb_file_stem,
            )
            for path_f in pr.resource_extract(
                generator_folder,
                path_dest,
                cb_suffix=cb_file_suffix,
                cb_file_stem=cb_file_stem,
                is_overwrite=True,
                as_user=True,
            ):
                self.assertTrue(issubclass(type(path_f), PurePath))
                self.assertTrue(path_f.exists() and path_f.is_file())
                self.assertTrue(path_f.parent, path_dest)

                """ Change file size

                    Will be immediately removing file, ok to
                    comprimise json format. Overt ur eyes,
                    if this is painful to watch
                """
                str_text = path_f.read_text()
                str_text = f"{str_text} asdfdsfaf adfaf dsf adsf"
                path_f.write_text(str_text)
                path_last_f = path_f

        # rm
        with suppress(Exception):
            if path_last_f is not None:
                path_last_f.unlink()

        # :py:func:`Path.rmdir`
        if path_dest.exists() and path_dest.is_dir():
            with suppress(Exception):
                path_dest.rmdir()

    def test_cache_extract(self):
        """Extract package resource to user cache folder"""
        pr = PackageResource(self.package_dest_c, self.fallback_package_base_folder)
        pr2 = PackageResource(self.package_dest_c, "bad_idea")

        # In cache_extract, provides destination folder. Will override this
        user_cache_dir_path = _extract_folder(pr.package)
        self.assertIsInstance(user_cache_dir_path, str)
        self.assertIn(str(Path.home()), user_cache_dir_path)

        valids = (
            (
                pr,
                partial(filter_by_file_stem, "mp_1_asz"),
                partial(filter_by_suffix, ".worker.logging.config.yaml"),
                1,
                1,
            ),
            (
                pr2,
                partial(filter_by_file_stem, "mp_1_shared"),
                partial(filter_by_suffix, ".worker.logging.config.yaml"),
                2,
                2,  # same file name. Source two different folders
            ),
        )
        for (
            pr_x,
            cb_file_stem,
            cb_file_suffix,
            folders_expected,
            files_expected,
        ) in valids:
            with (
                tempfile.TemporaryDirectory() as fp,
                patch(
                    "logging_strict.util.package_resource._extract_folder",
                    return_value=fp,
                ) as mock_folder,
            ):
                self.assertEqual(mock_folder.return_value, fp)

                gen = pr_x.package_data_folders(
                    cb_suffix=cb_file_suffix,
                    cb_file_stem=cb_file_stem,
                    path_relative_package_dir=pr_x.package_data_folder_start,
                )
                folders = list(gen)  # run generator
                folder_count = len(folders)
                self.assertEqual(folder_count, folders_expected)

                # refresh generator
                gen = pr_x.package_data_folders(
                    cb_suffix=cb_file_suffix,
                    cb_file_stem=cb_file_stem,
                    path_relative_package_dir=pr_x.package_data_folder_start,
                )

                gen_path = pr_x.cache_extract(
                    gen,
                    cb_suffix=cb_file_suffix,
                    cb_file_stem=cb_file_stem,
                )
                data_files = list(gen_path)  # run generator
                files_count = len(data_files)
                self.assertEqual(files_count, files_expected)
                self.assertTrue(data_files[0].exists())
                self.assertTrue(data_files[0].is_file())

    def test_package_data_folders(self):
        """Test PackageResource.package_data_folders"""
        pr = PackageResource(self.package_dest_c, self.fallback_package_base_folder)
        cb_file_stem = partial(filter_by_file_stem, "mp_1_asz")
        cb_file_suffix = partial(filter_by_suffix, ".worker.logging.config.yaml")

        app_names = (
            None,
            "",
            "    ",
            0.12345,
        )
        for app_name in app_names:
            gen = pr.package_data_folders(
                cb_suffix=cb_file_suffix,
                cb_file_stem=cb_file_stem,
            )
            folders = list(gen)
            folder_count = len(folders)
            self.assertNotEqual(folder_count, 0)
            del gen

        paths = (
            None,
            "",
            Path("data"),
            0.12345,
        )
        for mixed_path in paths:
            gen = pr.package_data_folders(
                cb_suffix=cb_file_suffix,
                cb_file_stem=cb_file_stem,
                path_relative_package_dir=mixed_path,
            )
            folders = list(gen)
            folder_count = len(folders)
            self.assertNotEqual(folder_count, 0)
            del gen

        # Adjust root folder -- str and relative Path
        cb_file_stem = partial(filter_by_file_stem, "mp_1_asz")
        cb_file_suffix = partial(filter_by_suffix, ".worker.logging.config.yaml")
        paths = (
            "configs",
            Path("configs"),
        )
        for mixed_path in paths:
            generator_folder = pr.package_data_folders(
                cb_suffix=cb_file_suffix,
                cb_file_stem=cb_file_stem,
                path_relative_package_dir=mixed_path,
            )
            # Exhausts generator
            is_generator_empty = len(list(generator_folder)) == 0

        self.assertTrue(not is_generator_empty)
        del generator_folder

        """ Package not installed; raise ImportError

            Keep in mind, normally the generator is passed as
            an argument to resource_extract or :py:func:`cache_extract`. Those
            functions log a warning and yield from an empty Iterator.
            In laymen terms, will yield nothing
        """
        pr2 = PackageResource(
            "adsfasdfdsafijdfiuhdsfihfdsgfg", self.fallback_package_base_folder
        )
        for mixed_path in paths:
            with self.assertRaises(ImportError):
                generator_folder = pr2.package_data_folders(
                    cb_suffix=cb_file_suffix,
                    cb_file_stem=cb_file_stem,
                    path_relative_package_dir=mixed_path,
                )
                # Run generator
                list(generator_folder)

    def test_is_package_exists(self) -> None:
        """Test module function is_package_exists"""
        self.assertTrue(is_package_exists(self.package_dest_c))
        package_name = "dsafdsafdsffdsdsa876d7f68745dfdsfy5rydsaf6r76f585dsaf"
        self.assertFalse(is_package_exists(package_name))

    def test_package_data_folders_problem(self) -> None:
        """I hate generators!

        Merely creating a generator does not run the generator.
        This generator raises an Exception when run. Just have to
        be careful to run it

        This applies, as well, to logging code within the generator
        """
        pr = PackageResource(self.package_dest_c, self.fallback_package_base_folder)
        pr2 = PackageResource(
            "dsafdsafdsffdsdsa876d7f68745dfdsfy5rydsaf6r76f585dsaf",
            self.fallback_package_base_folder,
        )
        cb_file_stem = partial(filter_by_file_stem, "mp_1_asz")
        cb_file_suffix = partial(filter_by_suffix, ".worker.logging.config.yaml")
        paths = (
            pr.package_data_folder_start,
            Path(pr.package_data_folder_start),
        )
        # package doesn't exist in virtual environment
        self.assertFalse(is_package_exists(pr2.package))

        # Does not execute the generator. No Exception yet
        for start_dir in paths:
            gen = pr2.package_data_folders(
                cb_suffix=cb_file_suffix,
                cb_file_stem=cb_file_stem,
                path_relative_package_dir=start_dir,
            )

            with self.assertRaises(ImportError):
                list(gen)  # Run the generator

        # nonexistent fallback to all package data folders
        # absolute path is ignored
        # :command:`openssl rand -hex 8`
        paths = [
            ("c8766a76e71756a47", 1),
            (Path("c8766a76e71756a47"), 1),
        ]
        if not platform.system().lower() == "windows":
            paths.append(("/etc/fstab", 1))
            paths.append((Path("/etc/fstab"), 1))

        for start_dir, expected_count in paths:
            gen = pr.package_data_folders(
                cb_suffix=cb_file_suffix,
                cb_file_stem=cb_file_stem,
                path_relative_package_dir=start_dir,
            )
            folders = list(gen)
            folder_count = len(folders)
            self.assertEqual(folder_count, expected_count)

    def test_walk_tree_folders(self):
        """What if no folders found?"""
        pr = PackageResource(self.package_dest_c, self.fallback_package_base_folder)
        self.assertTrue(is_package_exists(pr.package))
        trav_folder = _get_package_data_folder(f"{pr.package}.bad_idea.folder0")
        self.assertIsNotNone(trav_folder)
        gen = walk_tree_folders(trav_folder)
        folders = list(gen)
        folder_count = len(folders)
        self.assertEqual(folder_count, 0)


class PreviouslyUnitPath(unittest.TestCase):
    """Previously named something else. So what right."""

    def test_msg_stem(self) -> None:
        """Test module function msg_stem"""
        # None
        with self.assertRaises(ValueError):
            msg_stem(None)
        # empty string
        with self.assertRaises(ValueError):
            msg_stem("")
        paths = (
            Path("dsafdsaf.tar.gz"),
            "dsafdsaf.tar.gz",
            Path("dsafdsaf.tar"),
            "dsafdsaf.tar",
        )
        for mixed_path in paths:
            ret = msg_stem(mixed_path)
            self.assertIsInstance(ret, str)
            self.assertEqual(ret, "dsafdsaf")

        # No suffix
        mixed_path = "dsafdsaf"
        ret = msg_stem(mixed_path)
        self.assertIsInstance(ret, str)
        self.assertEqual(ret, "dsafdsaf")


class SanitizePackageName(unittest.TestCase):
    """Sanitizes package name."""

    def test_to_package_case(self):
        """Sanitize package name to a valid dotted path

        The ultimate test is
        :py:func:`logging_strict.util.package_resource._get_package_data_folder`.
        Which wraps :py:func:`importlib_resources.files`. Expects a dotted path.

        If :py:func:`importlib_resources.files` doesn't get a valid dotted path,
        returns None. Can be unexpected leading to hard to spot and/or
        track down issues.
        """
        t_package_names = (
            ("dog%food#yum!py", "dog_food_yum_py"),  # weird chars --> underscore
            ("dog-food_yum-py", "dog_food_yum_py"),  # hyphens --> underscore
            ("zope.interface", "zope.interface"),  # namespace package
        )
        for package_name, expected in t_package_names:
            actual = _to_package_case(package_name)
            self.assertEqual(actual, expected)


if __name__ == "__main__":  # pragma: no cover
    """Without coverage

    .. code-block:: shell

       python -m tests.test_util_package_resource --locals --verbose

       python -m unittest tests.test_util_package_resource \
       -k PackageResource.test_cache_extract --locals --verbose

       python -m unittest tests.test_util_package_resource \
       -k PackageResource.test_path_relative --locals --verbose

       python -m unittest tests.test_util_package_resource \
       -k PackageResource.test_get_parent_paths --locals --verbose

       python -m unittest tests.test_util_package_resource \
       -k PackageResource.test_resource_extract --locals --verbose

    With coverage
    .. code-block:: shell

       coverage run --data-file=".coverage-combine-11" \
       -m unittest discover -t. -s tests -p "test_util_package_resource*.py" --locals

       coverage report --include="**/util/package_resource*" --no-skip-covered \
       --data-file=".coverage-combine-11"

    """
    unittest.main()
