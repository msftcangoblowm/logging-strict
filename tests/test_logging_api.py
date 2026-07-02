"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

logging API is called by the main entrypoint

"""

import tempfile
import unittest
from collections.abc import Iterator
from pathlib import (
    Path,
    PurePath,
)
from typing import TYPE_CHECKING
from unittest.mock import (
    Mock,
    patch,
)

import strictyaml as s

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

if TYPE_CHECKING:
    from typing import Any


class LoggingApi(unittest.TestCase):
    """Test logging api interface."""

    def setUp(self) -> None:
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

    def test_setup_x(self) -> None:
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
            return None  # type: ignore[return-value]

        m_extract = Mock(spec_set=dummy)
        m_setup = Mock(spec=dummy_setup)

        """curated means in package logging_strict. Both are known:
        package name and relative path.

        package name only to redirect path during testing
        """
        valids_0 = (
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
        for func_0, package_name_0, genre_0, flavor_0, expectation_0 in valids_0:
            with (
                tempfile.TemporaryDirectory() as fp,
                patch(  # defang (redundant). extract_to_config
                    f"{g_app_name}.util.xdg_folder._get_path_config",
                    return_value=Path(fp),
                ),
                patch(  # temp folder rather than :code:`$HOME/.local/share/[app]`
                    f"{g_app_name}.logging_yaml_abc._get_path_config",
                    return_value=Path(fp).joinpath(package_name_0),
                ),
                patch(  # temp folder rather than :code:`$HOME/.local/share/[app]`
                    f"{g_app_name}.logging_api._get_path_config",
                    return_value=Path(fp).joinpath(package_name_0),
                ),
            ):
                # path_dest = Path(fp).joinpath(g_app_name, LoggingConfigYaml.file_name)
                with self.assertRaises(expectation_0):
                    func_0(
                        genre_0,
                        flavor_0,
                    )

        # ui_yaml_curated -- simulate success
        with patch(
            f"{g_app_name}.logging_api.setup_ui_other",
            return_value=("good", "job"),
        ):
            t_ret = ui_yaml_curated(
                "textual",
                "bob",
            )
            self.assertIsInstance(t_ret, tuple)
            self.assertEqual(len(t_ret), 2)

        """dummy extract causes FileNotFoundError. Spoofing being unable
        to find resource in package"""
        valids_1 = (
            (setup_ui_other, package_dest_c, "textual", "asz", FileNotFoundError),
            (setup_worker_other, package_dest_c, "mp", "asz", FileNotFoundError),
        )
        for func_1, package_name_1, genre_1, flavor_1, expectation_1 in valids_1:
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
                    return_value=Path(fp).joinpath(package_name_1),
                ),
                patch(  # temp folder rather than :code:`$HOME/.local/share/[app]`
                    f"{g_app_name}.logging_api._get_path_config",
                    return_value=Path(fp).joinpath(package_name_1),
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
                with self.assertRaises(expectation_1):
                    func_1(
                        package_name_1,
                        self.fallback_package_base_folder,
                        genre_1,
                        flavor_1,
                    )
                    mock_setup.assert_not_called()

                with self.assertRaises(LoggingStrictPackageNameRequired):
                    func_1(
                        None,  # type: ignore[arg-type]
                        self.fallback_package_base_folder,
                        genre_1,
                        flavor_1,
                    )

                with self.assertRaises(LoggingStrictPackageStartFolderNameRequired):
                    func_1(
                        package_name_1,
                        None,  # type: ignore[arg-type]
                        genre_1,
                        flavor_1,
                    )

        # Don't mock LoggingConfigYaml.extract. Test Exception conditions
        package_nonexistent = "sadfdsafdsafdsfdsafdsaffd"
        valids_2 = (
            (setup_ui_other, package_nonexistent, "textual", "asz", ImportError),
            (setup_worker_other, package_nonexistent, "mp", "asz", ImportError),
        )
        for func_2, package_name_2, genre_2, flavor_2, expectation_2 in valids_2:
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
                    return_value=Path(fp).joinpath(package_name_2),
                ),
                patch(  # temp folder rather than :code:`$HOME/.local/share/[app]`
                    f"{g_app_name}.logging_api._get_path_config",
                    return_value=Path(fp).joinpath(package_name_2),
                ),
                patch(  # replace with mock
                    f"{g_app_name}.logging_api.LoggingConfigYaml.setup",
                    new_callable=m_setup,
                ) as mock_setup,
            ):
                with self.assertRaises(expectation_2):
                    func_2(
                        package_name_2,
                        self.fallback_package_base_folder,
                        genre_2,
                        flavor_2,
                    )
                    mock_setup.assert_not_called()

        # Extract file
        #    Will actual extract file, so package must be real
        #    Normally 2nd party, not 1st party package
        valids_3 = (
            (setup_ui_other, self.package_dest_c, "textual", "asz"),
            (setup_worker_other, self.package_dest_c, "mp", "asz"),
        )
        for func_3, package_name_3, genre_3, flavor_3 in valids_3:
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
                    return_value=Path(fp).joinpath(package_name_3),
                ),
                patch(  # temp folder rather than :code:`$HOME/.local/share/[app]`
                    f"{g_app_name}.logging_api._get_path_config",
                    return_value=Path(fp).joinpath(package_name_3),
                ),
                patch(  # defang setup
                    f"{g_app_name}.logging_yaml_abc.setup_logging_yaml",
                    new_callable=m_setup,
                ) as mock_setup2,
            ):
                func_3(
                    package_name_3,
                    self.fallback_package_base_folder,
                    genre_3,
                    flavor_3,
                    package_start_relative_folder=self.fallback_package_base_folder,  # non-empty start dir
                )
                mock_setup2.assert_called()

                # simulate runtime validation fail
                with patch(
                    f"{g_app_name}.logging_yaml_abc.validate_yaml_dirty",
                    side_effect=s.YAMLValidationError(None, None, None),
                ):
                    with self.assertRaises(s.YAMLValidationError):
                        func_3(
                            package_name_3,
                            self.fallback_package_base_folder,
                            genre_3,
                            flavor_3,
                            package_start_relative_folder=self.fallback_package_base_folder,  # non-empty start dir
                        )

                # category not provided so file_stem cause problems
                api = LoggingConfigYaml(
                    package_name_3,
                    self.fallback_package_base_folder,
                    category=LoggingConfigCategory.UI,
                    genre=None,
                    flavor=flavor_3,
                )
                api.extract(
                    path_relative_package_dir="",
                )

                # category not provided so file_suffix cause problems
                api = LoggingConfigYaml(
                    package_name_3,
                    self.fallback_package_base_folder,
                    None,
                    genre=genre_3,
                    flavor=flavor_3,
                )
                api.extract(
                    path_relative_package_dir="",
                )

        # Package data issues: not found or not unique match
        #    nonexistent package --> ImportError
        package_nonexistent = "sadfdsafdsafdsfdsafdsaffd"
        valids_4 = (
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
            func_4,
            package_name_4,
            package_data_folder_start_4,
            genre_4,
            flavor_4,
            start_dir_4,
            exc_4,
        ) in valids_4:
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
                with self.assertRaises(exc_4):
                    func_4(
                        package_name_4,
                        package_data_folder_start_4,
                        genre_4,
                        flavor_4,
                        package_start_relative_folder=start_dir_4,
                    )

    def test_api_interface(self) -> None:
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
            flavor=flavor,  # type: ignore[arg-type]
            version_no=version,
        )
        self.assertEqual(api.file_stem, f"{genre}_{api.version}")

        # package not ok --> ValueError
        # package_data_folder_start not ok --> ValueError
        invalids_0 = (
            None,
            0.12345,
            "     ",
        )
        for invalid_0 in invalids_0:
            with self.assertRaises(ValueError):
                LoggingConfigYaml(
                    invalid_0,  # type: ignore[arg-type]
                    self.fallback_package_base_folder,
                    category=LoggingConfigCategory.UI,
                    genre=genre,
                    flavor=flavor,  # type: ignore[arg-type]
                    version_no=version,
                )
            with self.assertRaises(ValueError):
                LoggingConfigYaml(
                    self.package_dest_c,
                    invalid_0,  # type: ignore[arg-type]
                    category=LoggingConfigCategory.UI,
                    genre=genre,
                    flavor=flavor,  # type: ignore[arg-type]
                    version_no=version,
                )

        # genre not ok
        invalids_1 = (
            None,
            0.12345,
            "     ",
        )
        for invalid_1 in invalids_1:
            api = LoggingConfigYaml(
                self.package_dest_c,
                self.fallback_package_base_folder,
                category=LoggingConfigCategory.UI,
                genre=invalid_1,  # type: ignore[arg-type]
                flavor=flavor,  # type: ignore[arg-type]
                version_no=version,
            )

    def test_fcn_iter_yamls(self) -> None:
        """From a start path and given a pattern find all matching files"""
        if TYPE_CHECKING:
            kwargs_0: dict[Any, Any]
            kwargs_1: dict[Any, Any]
            kwargs_3: dict[Any, Any]

        # Within package, confirm yaml file count
        valids_0 = (
            (LoggingConfigCategory.UI.value, "textual", "asz", "1", 1),
            (LoggingConfigCategory.WORKER.value, "mp", "asz", "1", 1),
        )
        for category_0, genre_0, flavor_0, version_0, expected_count_0 in valids_0:
            api = LoggingConfigYaml(
                self.package_dest_c,
                self.fallback_package_base_folder,
                category=category_0,
                genre=genre_0,
                flavor=flavor_0,
                version_no=version_0,
            )
            args = (self.path_package_src,)
            kwargs_0 = {}

            pattern_actual = api.pattern(
                category=category_0,
                genre=genre_0,
                flavor=flavor_0,
                version=version_0,
            )
            pattern_expected = f"{genre_0}_{version_0}_{flavor_0}.{category_0}{LoggingConfigYaml.suffixes}"
            self.assertEqual(pattern_actual, pattern_expected)

            self.assertTrue(issubclass(type(self.path_package_src), PurePath))
            self.assertTrue(self.path_package_src.exists())
            self.assertTrue(self.path_package_src.is_dir())

            gen = api.iter_yamls(*args, **kwargs_0)
            self.assertIsInstance(gen, Iterator)
            files = list(gen)
            self.assertEqual(len(files), expected_count_0)
            del args, kwargs_0, gen

        # category unsupported type --> None --> ValueError
        invalids_1 = (
            (None, None, None, None, 0),
            (0.12345, 0.12345, 0.12345, 0.12345, 0),
        )
        package_name = self.package_dest_c
        # hardcoded: "configs"
        package_data_folder_start = self.fallback_package_base_folder
        for category_1, genre_1, flavor_1, version_1, _ in invalids_1:
            api = LoggingConfigYaml(
                package_name,
                package_data_folder_start,
                category=category_1,
                genre=genre_1,  # type: ignore[arg-type]
                flavor=flavor_1,  # type: ignore[arg-type]
                version_no=version_1,
            )
            """CI/CD environment has both src and build/lib off package base
            folder. Doubling file count. Don't pass in self.path_cwd
            """
            args_1 = (self.path_package_src,)
            kwargs_1 = {}
            gen = api.iter_yamls(*args_1, **kwargs_1)
            files = list(gen)
            file_count = len(files)
            self.assertEqual(file_count, 4)

        # path_dir None or unsupported type
        invalids_2 = (
            None,
            0.12345,
        )
        valids_2 = (
            (LoggingConfigCategory.UI.value, "textual", "asz", "1", 1),
            (LoggingConfigCategory.WORKER.value, "mp", "asz", "1", 1),
        )
        for category_2, genre_2, flavor_2, version_2, _ in valids_2:
            for invalid_2 in invalids_2:
                api = LoggingConfigYaml(
                    self.package_dest_c,
                    self.fallback_package_base_folder,
                    category=category_2,
                    genre=genre_2,
                    flavor=flavor_2,
                    version_no=version_2,
                )
                gen = api.iter_yamls(
                    invalid_2,  # type: ignore[arg-type]
                )
                self.assertIsInstance(gen, Iterator)
                files = list(gen)
                self.assertEqual(len(files), 0)

        # path_dir not exists or not a folder
        valids_3 = (
            (LoggingConfigCategory.UI.value, "textual", "asz", "1", 1),
            (LoggingConfigCategory.WORKER.value, "mp", "asz", "1", 1),
        )
        for category_3, genre_3, flavor_3, version_3, _ in valids_3:
            api = LoggingConfigYaml(  # <-- dies here
                self.package_dest_c,
                self.fallback_package_base_folder,
                category=category_3,
                genre=genre_3,
                flavor=flavor_3,
                version_no=version_3,
            )
            args = (self.path_package_src.joinpath("constants.py"),)
            kwargs_3 = {}
            gen = api.iter_yamls(*args, **kwargs_3)
            self.assertIsInstance(gen, Iterator)
            files = list(gen)
            self.assertEqual(len(files), 0)

    def test_file_name(self) -> None:
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

    def test_messing_with_logging_state(self) -> None:
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

        class NonSingleton:
            """A bare class with a dubious name"""

            pass

        # 1. Prove LoggingState IS a singleton
        state_1 = LoggingState()
        state_2 = LoggingState()
        self.assertIs(state_1, state_2)  # Mypy OK: Both are LoggingState

        # 2. Prove NonSingleton IS NOT a singleton
        non_1 = NonSingleton()
        non_2 = NonSingleton()
        self.assertIsNot(non_1, non_2)  # Mypy OK: Both are NonSingleton

        LoggingState.reset()
        self.assertTrue(LoggingState() is LoggingState())

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
                log_state.is_state_app = state_initial  # pyright: ignore[reportPossiblyUnboundVariable]  # fmt: skip


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
