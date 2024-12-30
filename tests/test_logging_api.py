"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

logging API is called by the main entrypoint

"""

import sys
import tempfile
import unittest
from pathlib import (
    Path,
    PurePath,
)
from unittest.mock import (
    Mock,
    patch,
)

from logging_strict import (
    LoggingConfigCategory,
    LoggingState,
    setup_ui_other,
    setup_worker_other,
    ui_yaml_curated,
    worker_yaml_curated,
)
from logging_strict.constants import g_app_name
from logging_strict.exceptions import (
    LoggingStrictGenreRequired,
    LoggingStrictPackageNameRequired,
    LoggingStrictPackageStartFolderNameRequired,
    LoggingStrictProcessCategoryRequired,
)
from logging_strict.logging_api import LoggingConfigYaml

if sys.version_info >= (3, 9):  # pragma: no cover
    from collections.abc import Iterator
else:  # pragma: no cover
    from typing import Iterator


class LoggingApi(unittest.TestCase):
    """Test logging api interface."""

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
        self.package_dest_c = g_app_name
        self.fallback_package_base_folder = "configs"

    def test_setup_x(self):
        """One liner to setup logging for a worker"""
        package_dest_c = "bar"

        # No extracted file, so setup skipped
        def dummy() -> str:
            """dummy function that has a local variable. Raises
            FileNotFoundError and ends in a return statement.

            Looks like a Frankensteign function meant for use with
            ``get_locals``. Break get_locals when the Exception is raised.
            """
            msg_err = "No yaml file found"
            raise FileNotFoundError(msg_err)
            return "within/package/relative/path/to/resource"

        def dummy_setup(str_yaml: str) -> bool:
            """Dummy logging YAML config setup function."""
            return None

        m_extract = Mock(spec_set=dummy)
        m_setup = Mock(spec=dummy_setup)

        """curated means in package logging_strict. Both are known:
        package name and relative path.

        package name only to redirect path during testing
        """
        valids = (
            (
                worker_yaml_curated,
                package_dest_c,
                "mp",
                "bob",
                FileNotFoundError,
            ),
            (
                ui_yaml_curated,
                package_dest_c,
                "textual",
                "bob",
                FileNotFoundError,
            ),
        )
        for func, package_name, genre, flavor, expectation in valids:
            with (
                tempfile.TemporaryDirectory() as fp,
                patch(  # defang (redundant). extract_to_config
                    f"{g_app_name}.util.xdg_folder._get_path_config",
                    return_value=Path(fp),
                ),
                patch(  # temp folder rather than :code:`$HOME/.local/share/[app]`
                    f"{g_app_name}.logging_yaml_abc._get_path_config",
                    return_value=Path(fp).joinpath(package_name),
                ),
                patch(  # temp folder rather than :code:`$HOME/.local/share/[app]`
                    f"{g_app_name}.logging_api._get_path_config",
                    return_value=Path(fp).joinpath(package_name),
                ),
            ):
                # path_dest = Path(fp).joinpath(g_app_name, LoggingConfigYaml.file_name)
                with self.assertRaises(expectation):
                    func(
                        genre,
                        flavor,
                    )

        """dummy extract causes FileNotFoundError. Spoofing being unable
        to find resource in package"""
        valids = (
            (setup_ui_other, package_dest_c, "textual", "asz", FileNotFoundError),
            (setup_worker_other, package_dest_c, "mp", "asz", FileNotFoundError),
        )
        for func, package_name, genre, flavor, expectation in valids:
            with (
                tempfile.TemporaryDirectory() as fp,
                patch(  # defang (redundant). extract_to_config
                    f"{g_app_name}.util.xdg_folder._get_path_config",
                    return_value=Path(fp),
                ),
                patch(  # defang
                    "logging.config.dictConfig",
                    return_value=True,
                ),
                patch(  # temp folder rather than :code:`$HOME/.local/share/[app]`
                    f"{g_app_name}.logging_yaml_abc._get_path_config",
                    return_value=Path(fp).joinpath(package_name),
                ),
                patch(  # temp folder rather than :code:`$HOME/.local/share/[app]`
                    f"{g_app_name}.logging_api._get_path_config",
                    return_value=Path(fp).joinpath(package_name),
                ),
                patch(  # replace with mock
                    f"{g_app_name}.logging_api.LoggingConfigYaml.extract",
                    new_callable=m_extract,
                ),
                patch(  # replace with mock
                    f"{g_app_name}.logging_api.LoggingConfigYaml.setup",
                    new_callable=m_setup,
                ) as mock_setup,
            ):
                # path_dest = Path(fp).joinpath(g_app_name, LoggingConfigYaml.file_name)
                with self.assertRaises(expectation):
                    func(
                        package_name,
                        self.fallback_package_base_folder,
                        genre,
                        flavor,
                    )
                    mock_setup.assert_not_called()

                with self.assertRaises(LoggingStrictPackageNameRequired):
                    func(
                        None,
                        self.fallback_package_base_folder,
                        genre,
                        flavor,
                    )

                with self.assertRaises(LoggingStrictPackageStartFolderNameRequired):
                    func(
                        package_name,
                        None,
                        genre,
                        flavor,
                    )

        # Don't mock LoggingConfigYaml.extract. Test Exception conditions
        package_nonexistent = "sadfdsafdsafdsfdsafdsaffd"
        valids = (
            (setup_ui_other, package_nonexistent, "textual", "asz", ImportError),
            (setup_worker_other, package_nonexistent, "mp", "asz", ImportError),
        )
        for func, package_name, genre, flavor, expectation in valids:
            with (
                tempfile.TemporaryDirectory() as fp,
                patch(  # defang (redundant). extract_to_config
                    f"{g_app_name}.util.xdg_folder._get_path_config",
                    return_value=Path(fp),
                ),
                patch(  # defang
                    "logging.config.dictConfig",
                    return_value=True,
                ),
                patch(  # temp folder rather than :code:`$HOME/.local/share/[app]`
                    f"{g_app_name}.logging_yaml_abc._get_path_config",
                    return_value=Path(fp).joinpath(package_name),
                ),
                patch(  # temp folder rather than :code:`$HOME/.local/share/[app]`
                    f"{g_app_name}.logging_api._get_path_config",
                    return_value=Path(fp).joinpath(package_name),
                ),
                patch(  # replace with mock
                    f"{g_app_name}.logging_api.LoggingConfigYaml.setup",
                    new_callable=m_setup,
                ) as mock_setup,
            ):
                with self.assertRaises(expectation):
                    func(
                        package_name,
                        self.fallback_package_base_folder,
                        genre,
                        flavor,
                    )
                    mock_setup.assert_not_called()

        # Extract file
        #    Will actual extract file, so package must be real
        #    Normally 2nd party, not 1st party package
        valids = (
            (setup_ui_other, self.package_dest_c, "textual", "asz"),
            (setup_worker_other, self.package_dest_c, "mp", "asz"),
        )
        for func, package_name, genre, flavor in valids:
            with (
                tempfile.TemporaryDirectory() as fp,
                patch(  # defang. extract_to_config
                    f"{g_app_name}.util.xdg_folder._get_path_config",
                    return_value=Path(fp),
                ),
                patch(  # defang
                    "logging.config.dictConfig",
                    return_value=True,
                ),
                patch(  # temp folder rather than :code:`$HOME/.local/share/[app]`
                    f"{g_app_name}.logging_yaml_abc._get_path_config",
                    return_value=Path(fp).joinpath(package_name),
                ),
                patch(  # temp folder rather than :code:`$HOME/.local/share/[app]`
                    f"{g_app_name}.logging_api._get_path_config",
                    return_value=Path(fp).joinpath(package_name),
                ),
                patch(  # defang setup
                    f"{g_app_name}.logging_yaml_abc.setup_logging_yaml",
                    new_callable=m_setup,
                ) as mock_setup2,
            ):
                func(
                    package_name,
                    self.fallback_package_base_folder,
                    genre,
                    flavor,
                    package_start_relative_folder=self.fallback_package_base_folder,  # non-empty start dir
                )
                mock_setup2.assert_called()

                # category not provided so file_stem cause problems
                api = LoggingConfigYaml(
                    package_name,
                    self.fallback_package_base_folder,
                    category=LoggingConfigCategory.UI,
                    genre=None,
                    flavor=flavor,
                )
                api.extract(
                    path_relative_package_dir="",
                )

                # category not provided so file_suffix cause problems
                api = LoggingConfigYaml(
                    package_name,
                    self.fallback_package_base_folder,
                    None,
                    genre=genre,
                    flavor=flavor,
                )
                api.extract(
                    path_relative_package_dir="",
                )

        # Package data issues: not found or not unique match
        #    nonexistent package --> ImportError
        package_nonexistent = "sadfdsafdsafdsfdsafdsaffd"
        valids = (
            (  # not found in package
                setup_ui_other,
                package_nonexistent,
                self.fallback_package_base_folder,
                "poor",
                "asz",
                self.fallback_package_base_folder,
                ImportError,
            ),
            (  # not found in package
                setup_ui_other,
                self.package_dest_c,
                self.fallback_package_base_folder,
                "poor",
                "asz",
                self.fallback_package_base_folder,
                FileNotFoundError,
            ),
            (  # not found in package
                setup_worker_other,
                self.package_dest_c,
                self.fallback_package_base_folder,
                "mp",
                "godzilla-vs-mothra-in-funny-face-no-laugh-contest",
                self.fallback_package_base_folder,
                FileNotFoundError,
            ),
            (  # not found in package. Start search at base folder
                setup_worker_other,
                self.package_dest_c,
                self.fallback_package_base_folder,
                "mp",
                "godzilla-vs-mothra-in-funny-face-no-laugh-contest",
                "",
                FileNotFoundError,
            ),
            (  # multiple found
                setup_worker_other,
                self.package_dest_c,
                "bad_idea",
                "mp",
                "shared",
                "bad_idea",
                AssertionError,
            ),
        )
        for (
            func,
            package_name,
            package_data_folder_start,
            genre,
            flavor,
            start_dir,
            exc,
        ) in valids:
            with (
                tempfile.TemporaryDirectory() as fp,
                patch(  # defang. extract_to_config
                    f"{g_app_name}.util.xdg_folder._get_path_config",
                    return_value=Path(fp),
                ),
                patch(  # defang
                    "logging.config.dictConfig",
                    return_value=True,
                ),
                patch(  # temp folder rather than :code:`$HOME/.local/share/[app]`
                    f"{g_app_name}.logging_yaml_abc._get_path_config",
                    return_value=Path(fp).joinpath(package_dest_c),
                ),
                patch(  # temp folder rather than :code:`$HOME/.local/share/[app]`
                    f"{g_app_name}.logging_api._get_path_config",
                    return_value=Path(fp).joinpath(package_dest_c),
                ),
                patch(  # defang setup
                    f"{g_app_name}.logging_yaml_abc.setup_logging_yaml",
                    new_callable=m_setup,
                ),
            ):
                with self.assertRaises(exc):
                    func(
                        package_name,
                        package_data_folder_start,
                        genre,
                        flavor,
                        package_start_relative_folder=start_dir,
                    )

    def test_api_interface(self):
        """LoggingConfigYaml interface"""
        # Test properties file_stem and version
        genre = "textual"
        flavor = 0.12345  # unsupported --> no flavor
        version = 0.12345  # version --> fallback
        api = LoggingConfigYaml(
            self.package_dest_c,
            self.fallback_package_base_folder,
            category=LoggingConfigCategory.UI,
            genre=genre,
            flavor=flavor,
            version_no=version,
        )
        self.assertEqual(api.file_stem, f"{genre}_{api.version}")

        # package not ok --> ValueError
        # package_data_folder_start not ok --> ValueError
        invalids = (
            None,
            0.12345,
            "     ",
        )
        for invalid in invalids:
            with self.assertRaises(ValueError):
                LoggingConfigYaml(
                    invalid,
                    self.fallback_package_base_folder,
                    category=LoggingConfigCategory.UI,
                    genre=genre,
                    flavor=flavor,
                    version_no=version,
                )
            with self.assertRaises(ValueError):
                LoggingConfigYaml(
                    self.package_dest_c,
                    invalid,
                    category=LoggingConfigCategory.UI,
                    genre=genre,
                    flavor=flavor,
                    version_no=version,
                )

        # genre not ok
        invalids = (
            None,
            0.12345,
            "     ",
        )
        for invalid in invalids:
            api = LoggingConfigYaml(
                self.package_dest_c,
                self.fallback_package_base_folder,
                category=LoggingConfigCategory.UI,
                genre=invalid,
                flavor=flavor,
                version_no=version,
            )

    def test_fcn_iter_yamls(self):
        """From a start path and given a pattern find all matching files"""

        # Within package, confirm yaml file count
        valids = (
            (LoggingConfigCategory.UI.value, "textual", "asz", "1", 1),
            (LoggingConfigCategory.WORKER.value, "mp", "asz", "1", 1),
        )
        for category, genre, flavor, version, expected_count in valids:
            api = LoggingConfigYaml(
                self.package_dest_c,
                self.fallback_package_base_folder,
                category=category,
                genre=genre,
                flavor=flavor,
                version_no=version,
            )
            args = (self.path_package_src,)
            kwargs = {}

            pattern_actual = api.pattern(
                category=category,
                genre=genre,
                flavor=flavor,
                version=version,
            )
            pattern_expected = (
                f"{genre}_{version}_{flavor}.{category}{LoggingConfigYaml.suffixes}"
            )
            self.assertEqual(pattern_actual, pattern_expected)

            self.assertTrue(issubclass(type(self.path_package_src), PurePath))
            self.assertTrue(self.path_package_src.exists())
            self.assertTrue(self.path_package_src.is_dir())

            gen = api.iter_yamls(*args, **kwargs)
            self.assertIsInstance(gen, Iterator)
            files = list(gen)
            self.assertEqual(len(files), expected_count)
            del args, kwargs, gen

        # category unsupported type --> None --> ValueError
        invalids = (
            (None, None, None, None, 0),
            (0.12345, 0.12345, 0.12345, 0.12345, 0),
        )
        package_name = self.package_dest_c
        # hardcoded: "configs"
        package_data_folder_start = self.fallback_package_base_folder
        for category2, genre2, flavor2, version2, expected_count2 in invalids:
            api = LoggingConfigYaml(
                package_name,
                package_data_folder_start,
                category=category2,
                genre=genre2,
                flavor=flavor2,
                version_no=version2,
            )
            """CI/CD environment has both src and build/lib off package base
            folder. Doubling file count. Don't pass in self.path_cwd
            """
            args2 = (self.path_package_src,)
            kwargs2 = {}
            gen = api.iter_yamls(*args2, **kwargs2)
            files = list(gen)
            file_count = len(files)
            self.assertEqual(file_count, 4)

        # path_dir None or unsupported type
        invalids = (
            None,
            0.12345,
        )
        valids = (
            (LoggingConfigCategory.UI.value, "textual", "asz", "1", 1),
            (LoggingConfigCategory.WORKER.value, "mp", "asz", "1", 1),
        )
        for category, genre, flavor, version, expected_count in valids:
            for invalid in invalids:
                api = LoggingConfigYaml(
                    self.package_dest_c,
                    self.fallback_package_base_folder,
                    category=category,
                    genre=genre,
                    flavor=flavor,
                    version_no=version,
                )
                gen = api.iter_yamls(
                    invalid,
                )
                self.assertIsInstance(gen, Iterator)
                files = list(gen)
                self.assertEqual(len(files), 0)

        # path_dir not exists or not a folder
        valids = (
            (LoggingConfigCategory.UI.value, "textual", "asz", "1", 1),
            (LoggingConfigCategory.WORKER.value, "mp", "asz", "1", 1),
        )
        for category, genre, flavor, version, expected_count in valids:
            api = LoggingConfigYaml(  # <-- dies here
                self.package_dest_c,
                self.fallback_package_base_folder,
                category=category,
                genre=genre,
                flavor=flavor,
                version_no=version,
            )
            args = (self.path_package_src.joinpath("constants.py"),)
            kwargs = {}
            gen = api.iter_yamls(*args, **kwargs)
            self.assertIsInstance(gen, Iterator)
            files = list(gen)
            self.assertEqual(len(files), 0)

    def test_file_name(self):
        """file_name property needs both category and genre"""
        category = LoggingConfigCategory.UI.value
        genre = "textual"
        flavor = "asz"
        version = "1"

        # file_stem issue cuz no genre
        api = LoggingConfigYaml(
            self.package_dest_c,
            self.fallback_package_base_folder,
            category,
            genre=None,
            flavor=flavor,
            version_no=version,
        )
        with self.assertRaises(LoggingStrictGenreRequired):
            api.file_name

        # file_suffix issue cuz no category
        api = LoggingConfigYaml(
            self.package_dest_c,
            self.fallback_package_base_folder,
            None,
            genre=genre,
            flavor=flavor,
            version_no=version,
        )
        with self.assertRaises(LoggingStrictProcessCategoryRequired):
            api.file_name


class SharedResourceLogger(unittest.TestCase):
    """The unittest features are implemented as a ThreadPool, so the
    logging state is shared. This is not ideal.

    The best solution is to refactor and implement as a
    :py:class:`multiprocessing.pool.Pool`.
    In the meantime, stuck with the less than ideal situation
    (ThreadPool implementation), not the situation would like to have.

    This unittest can be run from:

    - cli
    - ui (unittest module, class, or function screens). ThreadPool
    - ui (recipe screen). :py:class:`multiprocessing.pool.Pool`

    Messing with logging is a bad idea and dirty, each
    :py:class:`logger.Logger` is a Singleton so hangs around forever
    """

    def test_messing_with_logging_state(self):
        """Mess with a Singleton. Scary and a bad idea"""

        # The state to return the Singleton to
        with LoggingState._lock:
            if LoggingState._instance is None:
                log_state_inst = None
            else:
                log_state_inst = LoggingState()
                LoggingState()
                state_initial = log_state_inst.is_state_app

        # is_state_app=bool
        valids = (
            True,
            False,
        )
        for valid in valids:
            LoggingState.reset()
            self.assertIsNone(LoggingState._instance)
            log_state = LoggingState()
            log_state.is_state_app = valid
            self.assertEqual(log_state.is_state_app, valid)

        # is_state_app=None
        LoggingState.reset()
        log_state = LoggingState()
        log_state.is_state_app = None
        self.assertFalse(log_state.is_state_app)
        # is_state_app=invalids (non-booleans)
        invalids = (
            None,
            "",
            0.12345,  # float is not a bool, eventhough easy to convert
            1,
            0,
        )
        for invalid in invalids:
            LoggingState.reset()
            log_state = LoggingState()
            log_state.is_state_app = invalid
            self.assertFalse(log_state.is_state_app)

        # Confirm it's a Singleton
        LoggingState.reset()
        self.assertTrue(LoggingState() is LoggingState())

        class NonSingleton:
            """A bare class with a dubious name"""

            pass

        self.assertTrue(LoggingState() is not NonSingleton())

        # Get current log state. Is run as app or from cli?
        LoggingState.reset()
        log_state = LoggingState()
        log_state.is_state_app = True
        state_current = log_state.is_state_app
        self.assertIsInstance(state_current, bool)
        self.assertTrue(state_current)

        # Set log state
        invalids = (
            None,
            "",
            0.12345,  # float is not a bool, eventhough easy to convert
            1,
            0,
        )
        for invalid in invalids:
            log_state.is_state_app = invalid
            # Confirm state hasn't changed
            self.assertEqual(log_state.is_state_app, state_current)

        # Toggle state twice
        state_before = log_state.is_state_app
        log_state.is_state_app = not log_state.is_state_app
        log_state.is_state_app = not log_state.is_state_app
        state_after = log_state.is_state_app
        self.assertEqual(state_before, state_after)

        # Return to initial state
        # The state to return the Singleton to
        if log_state_inst is None:
            LoggingState.reset()
        else:
            with LoggingState._lock:
                LoggingState._instance = log_state_inst
                log_state = LoggingState()
                log_state.is_state_app = state_initial


if __name__ == "__main__":  # pragma: no cover
    """Without coverage
    .. code-block:: shell

       python -m tests.test_logging_api --locals

       python -m unittest tests.test_logging_api \
       -k LoggingApi.test_setup_x --locals --verbose

       python -m unittest tests.test_logging_api \
       -k LoggingApi.test_api_interface --locals --verbose

       python -m unittest tests.test_logging_api \
       -k LoggingApi.test_fcn_iter_yamls --locals --verbose

       python -m unittest tests.test_logging_api \
       -k LoggingApi.test_file_name --locals --verbose

    With coverage

    .. code-block:: shell

       coverage run --data-file=".coverage-combine-33" \
       -m unittest discover -t. -s tests -p "test_logging_api*.py" --locals

       coverage report --include="*logging_api*" --no-skip-covered \
       --data-file=".coverage-combine-33"

       coverage report --data-file=".coverage-combine-33" --no-skip-covered

    """
    unittest.main(tb_locals=True)
