"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

``logging_strict.yml`` registry db holds one record per logging config YAML file.
Both the ``logging_strict.yml`` and a ``*.logging.config.yaml`` are extracted.

No longer need to know:

- which package subfolder holds each ``*.logging.config.yaml`` file.

- :py:func:`unittest.mock.patch` the extraction destination folder
whilst testing or by ``pytest-logging-strict``

"""

import tempfile
import unittest
from collections.abc import Sequence
from contextlib import nullcontext as does_not_raise
from contextlib import suppress
from pathlib import (
    Path,
    PurePath,
)
from unittest.mock import (
    PropertyMock,
    patch,
)

import strictyaml as s

from logging_strict import LoggingConfigCategory
from logging_strict.constants import g_app_name
from logging_strict.register_config import ExtractorLoggingConfig
from logging_strict.tech_niques import captureLogs


class TestExtractor(unittest.TestCase):
    """Improved Intuitive UI for extracting registry and logging config YAML files"""

    def setUp(self):
        """Initialize variables for test base folder and package base folder."""
        if "__pycache__" in __file__:
            # cached
            path_tests = Path(__file__).parent.parent
        else:
            # not cached
            path_tests = Path(__file__).parent

        self.path_cwd = path_tests.parent
        self.path_package_src = self.path_cwd.joinpath("src", g_app_name)
        self.package_name_raw = g_app_name

    def test_query_db_without_extract(self):
        """Extract never occurred"""
        category = LoggingConfigCategory.UI.value
        with tempfile.TemporaryDirectory() as fp:
            reg = ExtractorLoggingConfig(
                self.package_name_raw,
                path_alternative_dest_folder=Path(fp),
                is_test_file=False,
            )
            reg.query_db(category)
            self.assertIsNone(reg.path_extracted_db)
            self.assertIsNone(reg._registry)
            self.assertIsNone(reg.logging_config_yaml_str)
            self.assertIsNone(reg.logging_config_yaml_relpath)

    def test_query_db_xdg_folder(self):
        """Extracts to XDG folder"""
        # relative path --> xdg folder
        reg_0 = ExtractorLoggingConfig(  # noqa: F841
            self.package_name_raw,
            path_alternative_dest_folder=Path("configs"),
            is_test_file=0.12345,
        )

        # not str or path --> xdg folder
        reg_1 = ExtractorLoggingConfig(  # noqa: F841
            self.package_name_raw,
            path_alternative_dest_folder=0.12345,
            is_test_file=None,
        )

        # extract xdg folder
        category = LoggingConfigCategory.UI.value
        reg = ExtractorLoggingConfig(
            self.package_name_raw,
            path_alternative_dest_folder=None,
            is_test_file=False,
        )
        reg.get_db()
        with patch(  # defang
            "logging.config.dictConfig",
            return_value=True,
        ):
            reg.query_db(
                category,
                genre="textual",
                flavor="asz",
                version_no="1",
                logger_package_name=g_app_name,
            )

        """
        print(f"reg._path_extracted_db {reg._path_extracted_db!r}", file=sys.stderr)
        print(f"reg._path_extraction_dir {reg._path_extraction_dir!r}", file=sys.stderr)
        print(f"reg.logging_config_yaml_str {reg.logging_config_yaml_str!r}", file=sys.stderr)
        print(f"reg.logging_config_yaml_relpath {reg.logging_config_yaml_relpath!r}", file=sys.stderr)
        """
        pass

        """reg.logging_config_yaml_relpath is potentially user input,
        refrain from unlink file"""
        """
        path_f = reg._path_extraction_dir.joinpath(
            Path(reg.logging_config_yaml_relpath).as_posix(),
        )
        """

    def test_extract_db(self):
        """Extract and validate registry"""
        testdata = (
            (None, None, False, False, "path_alternative_dest_folder is None"),
            (None, True, False, True, "is_test_file True"),
        )
        for (
            path_alternative_dest_folder,
            is_test_file,
            is_patch_extract_folder,
            is_test_file_expected,
            testitem_desc,
        ) in testdata:
            reg = ExtractorLoggingConfig(
                self.package_name_raw,
                path_alternative_dest_folder=path_alternative_dest_folder,
                is_test_file=is_test_file,
            )
            self.assertEqual(reg._is_test_file, is_test_file_expected)
            self.assertEqual(reg._patch_extract_folder, is_patch_extract_folder)
            # private variable initialized
            self.assertIsNone(reg._path_extracted_db)
            self.assertIsNone(reg._logging_config_yaml_str)
            # ExtractorLoggingConfig.__repr__
            self.assertIsInstance(repr(reg), str)

        # path_alternative_dest_folder is a Path
        with tempfile.TemporaryDirectory() as fp:
            valids = (
                (str(fp), True),
                (str(fp), False),
                (Path(fp), True),
                (Path(fp), False),
            )
            for path_alternative_dest_folder, is_test_file in valids:
                reg = ExtractorLoggingConfig(
                    self.package_name_raw,
                    path_alternative_dest_folder=path_alternative_dest_folder,
                    is_test_file=is_test_file,
                )
                self.assertTrue(reg._patch_extract_folder)
                self.assertIsNone(reg.path_extracted_db)
                self.assertEqual(reg.is_test_file, is_test_file)
                reg.extract_db()
                self.assertIsNotNone(reg.path_extracted_db)
                self.assertTrue(issubclass(type(reg.path_extracted_db), PurePath))

        # Cause ImportError, by attempting to extract nonexistent package data file
        with (
            tempfile.TemporaryDirectory() as fp,
            patch(
                f"{g_app_name}.register_config.CONFIG_SUFFIX",
                return_value=".toml",
            ),
        ):
            testdata = ((Path(fp), False),)
            for path_alternative_dest_folder, is_test_file in testdata:
                reg = ExtractorLoggingConfig(
                    "sdfsadfsdafsadfsadfsadfy",
                    path_alternative_dest_folder=path_alternative_dest_folder,
                    is_test_file=is_test_file,
                )
                # logs INFO and WARNING messages. So capture at INFO level
                with captureLogs(logger=None, level=20) as cm:
                    reg.extract_db()
                out = cm.output
                msg_count_actual = len(out)
                msg_count_expected = 2
                self.assertEqual(msg_count_actual, msg_count_expected)
                self.assertIsNone(reg.path_extracted_db)

    def test_get_db(self):
        """Extract db and validate YAML

        .. seealso::

           :py:class:`unittest.mock.PropertyMock`

        """
        is_test_file = False
        with tempfile.TemporaryDirectory() as fp:
            path_alternative_dest_folder = Path(fp)

            # simulate extract_db failure. So property path_extracted_db would be None
            with patch(
                f"{g_app_name}.register_config.ExtractorLoggingConfig.path_extracted_db",
                new_callable=PropertyMock,
            ) as m:
                m.return_value = None
                reg = ExtractorLoggingConfig(
                    self.package_name_raw,
                    path_alternative_dest_folder=path_alternative_dest_folder,
                    is_test_file=is_test_file,
                )
                reg.get_db()
                self.assertIsNone(reg._registry)

            reg = ExtractorLoggingConfig(
                self.package_name_raw,
                path_alternative_dest_folder=path_alternative_dest_folder,
                is_test_file=is_test_file,
            )
            # simulate YAML validation failure
            with (
                patch(
                    f"{g_app_name}.register_config.validate_yaml_dirty",
                    side_effect=s.YAMLValidationError(None, None, None),
                ),
                self.assertRaises(s.YAMLValidationError),
            ):
                reg.get_db()
            self.assertIsNotNone(reg.path_extracted_db)
            self.assertIsNone(reg._registry)

            # Run it normally
            reg.get_db()
            self.assertIsNotNone(reg.path_extracted_db)
            self.assertIsNotNone(reg._registry)
            #    registry is implemented as a in YAML file, not a proper RDMS
            self.assertIsInstance(reg._registry, Sequence)
            self.assertIsNone(reg.logging_config_yaml_str)

    def test_query_two_step(self):
        """Two step process. extract_db then pass path to get_db"""
        # unsupported type --> extract_db called
        #    logs INFO and WARNING messages. So capture at INFO level
        with tempfile.TemporaryDirectory() as fp_0:
            reg_0 = ExtractorLoggingConfig(
                g_app_name,
                path_alternative_dest_folder=Path(fp_0),
                is_test_file=True,
            )
            with captureLogs(logger=None, level=20):
                reg_0.get_db(path_extracted_db=0.12345)
            ls_path_extracted_db = reg_0.path_extracted_db
            self.assertIsNotNone(ls_path_extracted_db)
            self.assertTrue(issubclass(type(ls_path_extracted_db), PurePath))
            self.assertTrue(ls_path_extracted_db.is_file())
            # cleanup
            # with suppress(OSError):
            #     fp_0.cleanup()

        # two step
        #    logs INFO and WARNING messages. So capture at INFO level
        with tempfile.TemporaryDirectory() as fp_1:
            reg_1 = ExtractorLoggingConfig(
                g_app_name,
                path_alternative_dest_folder=Path(fp_1),
                is_test_file=True,
            )
            with captureLogs(logger=None, level=20):
                reg_1.extract_db()
            ls_path_extracted_db = reg_1.path_extracted_db
            self.assertIsNotNone(ls_path_extracted_db)
            self.assertTrue(issubclass(type(ls_path_extracted_db), PurePath))
            self.assertTrue(ls_path_extracted_db.is_file())
            reg_1.get_db(path_extracted_db=ls_path_extracted_db)
            self.assertIsNotNone(reg_1._registry)
            # cleanup
            # with suppress(OSError):
            #    fp_1.cleanup()

    def test_query_db_main(self):
        """Query the registry db extracts returns validated logging config as str"""
        testdata = (
            (
                self.package_name_raw,
                LoggingConfigCategory.UI.value,
                "textual",
                None,
                None,
                "sprouts",
                False,
                "category and genre search app textual",
                does_not_raise(),
                True,
                True,
                False,
            ),
            (
                self.package_name_raw,
                LoggingConfigCategory.WORKER.value,
                "mp",
                None,
                None,
                "sprouts",
                False,
                "category and genre search. worker mp",
                does_not_raise(),
                True,
                False,
                False,
            ),
            (
                self.package_name_raw,
                LoggingConfigCategory.UI.value,
                "textual",
                None,
                None,
                None,
                False,
                "category and genre search. In yaml file, skip replacing package name",
                does_not_raise(),
                True,
                True,
                False,
            ),
            (
                self.package_name_raw,
                LoggingConfigCategory.UI.value,
                "textual",
                "dogfood",
                None,
                g_app_name,
                True,
                "category and genre and flavor search. No match",
                does_not_raise(),
                False,
                True,
                False,
            ),
            (
                self.package_name_raw,
                LoggingConfigCategory.WORKER.value,
                "dogfood",
                None,
                None,
                "sprouts",
                False,
                "Query too narrow. genre not found",
                does_not_raise(),
                False,
                False,
                False,
            ),
            (
                self.package_name_raw,
                LoggingConfigCategory.WORKER.value,
                "mp",
                "dogfood",
                None,
                "sprouts",
                False,
                "Query too narrow. flavor not found",
                does_not_raise(),
                False,
                False,
                False,
            ),
            (
                self.package_name_raw,
                LoggingConfigCategory.WORKER.value,
                "mp",
                "asz",
                "666",
                "sprouts",
                False,
                "Query too narrow. version_no not found",
                does_not_raise(),
                False,
                False,
                False,
            ),
            (
                self.package_name_raw,
                LoggingConfigCategory.WORKER.value,
                "mp",
                "shared",
                "1",
                g_app_name,
                True,
                "want test file but multiple folders --> AssertionError --> continue",
                does_not_raise(),
                False,
                True,
                False,
            ),
            (
                "sadfasdfasdfsdfsadfdsafiadsfkijufd",
                LoggingConfigCategory.UI.value,
                "textual",
                None,
                None,
                g_app_name,
                True,
                "no such package",
                does_not_raise(),
                False,
                True,
                True,
            ),
        )
        for idx, (
            package_name_raw,
            category,
            genre,
            flavor,
            version_no,
            logger_package_name,
            is_test_file,
            _,
            expectation,
            has_search_result,
            is_skip_setup,
            has_log_messages,
        ) in enumerate(testdata):
            with tempfile.NamedTemporaryFile(delete=False) as fp:
                path_f = Path(fp.name)
                path_alternative_dest_folder = path_f.parent
                # delete the file. Want option to not delete the folder
                with suppress(OSError):
                    path_f.unlink()

                reg = ExtractorLoggingConfig(
                    package_name_raw,
                    path_alternative_dest_folder=path_alternative_dest_folder,
                    is_test_file=is_test_file,
                )

                # Was there a is_test_file switcharoo?
                reg_is_test_file = reg.is_test_file  # noqa: F841
                self.assertEqual(
                    is_test_file,
                    reg.is_test_file,
                    msg="is_test_file switcharoo occurred",
                )

                # Check registry db valid
                with captureLogs(logger=None, level=20):
                    reg.get_db()
                reg_path_extracted_db = reg.path_extracted_db  # noqa: F841
                """
                self.assertIsNotNone(
                    reg_path_extracted_db,
                    msg="registry db not extracted",
                )
                """
                reg_registry = reg._registry  # noqa: F841
                # self.assertIsNotNone(reg_registry, msg="registry db yaml invalid?")

                # does not emit any log messages, get_db does
                reg.query_db(
                    category,
                    genre=genre,
                    flavor=flavor,
                    version_no=version_no,
                    logger_package_name=logger_package_name,
                    is_skip_setup=is_skip_setup,
                )
                if not isinstance(expectation, does_not_raise):
                    # e.g. ImportError
                    self.assertIsNone(reg.logging_config_yaml_str)
                    self.assertIsNone(reg.logging_config_yaml_relpath)
                else:
                    if not has_search_result:
                        self.assertIsNone(reg.logging_config_yaml_str)
                        self.assertIsNone(reg.logging_config_yaml_relpath)
                    else:
                        self.assertIsNotNone(reg.logging_config_yaml_str)
                        self.assertIsInstance(reg.logging_config_yaml_str, str)
                        # cleanup
                        logging_config_yaml_relpath = reg.logging_config_yaml_relpath
                        self.assertIsNotNone(logging_config_yaml_relpath)
                        self.assertIsInstance(logging_config_yaml_relpath, str)
                        # relpath uses pathlib.as_posix, not str
                        relpath_f = Path(logging_config_yaml_relpath)
                        abspath_f = path_alternative_dest_folder.joinpath(relpath_f)
                        with suppress(OSError):
                            abspath_f.unlink()


if __name__ == "__main__":  # pragma: no cover
    """Without coverage

    .. code-block:: shell

       python -m tests.test_registry_config --locals

       python -m unittest tests.test_registry_config \
       -k TestExtractor.test_query_db_main --locals --verbose

       python -m unittest tests.test_registry_config \
       -k TestExtractor.test_query_db_without_extract --locals --verbose

       python -m unittest tests.test_registry_config \
       -k TestExtractor.test_query_db_xdg_folder --locals --verbose

       python -m unittest tests.test_registry_config \
       -k TestExtractor.test_extract_db --locals --verbose

       python -m unittest tests.test_registry_config \
       -k TestExtractor.test_query_two_step --locals --verbose

    With coverage

    .. code-block:: shell

       coverage run --data-file=".coverage-combine-45" \
       -m unittest discover -t. -s tests -p "test_registry_config*.py" --locals

       coverage report --data-file=".coverage-combine-45" --no-skip-covered

    """
    unittest.main(tb_locals=True)
