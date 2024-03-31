"""
.. py:data:: g_package_second_party
   :type: str
   :value: "asz"

   This package (A) is a library or a dependency of another package
   (B). The logging config applies to B, not A

"""

from __future__ import annotations

import sys
import tempfile
import unittest
from functools import partial
from pathlib import Path
from typing import Optional
from unittest.mock import patch

import strictyaml as s

from logging_strict import (
    LoggingYamlType,
    setup_logging_yaml,
)
from logging_strict.constants import g_app_name
from logging_strict.exceptions import LoggingStrictGenreRequired
from logging_strict.logging_api_test import (
    MyLogger,
    file_name,
    g_package_second_party,
)
from logging_strict.logging_yaml_abc import VERSION_FALLBACK
from logging_strict.tech_niques import (
    ClassAttribTypes,
    get_locals,
    is_class_attrib_kind,
)

if sys.version_info >= (3, 9):  # pragma: no cover
    from collections.abc import Iterator
else:  # pragma: no cover
    from typing import Iterator


def cb_joinpath(fp: Path, x: str) -> Path:
    return Path(fp).joinpath(x)


class LoggingWorker(unittest.TestCase):
    def setUp(self):
        self.g_package_second_party = g_package_second_party
        self.yaml_worker = (
            "version: 1\n"
            "disable_existing_loggers: false\n"
            "raise_exceptions: true\n"
            "formatters:\n"
            "  detailed:\n"
            "    class: logging.Formatter\n"
            """    format: '%(asctime)s %(name)-15s %(levelname)-8s """
            """%(processName)-10s %(message)s'\n"""
            "  simple:\n"
            "    class: logging.Formatter\n"
            """    format: '%(name)-15s %(levelname)-8s """
            """%(processName)-10s %(message)s'\n"""
            "handlers:\n"
            "  console_worker:\n"
            "    class: logging.StreamHandler\n"
            "    formatter: simple\n"
            "    level: WARNING\n"
            "loggers:\n"
            "  asz:\n"
            "    handlers: [console_worker]\n"
            "    propagate: yes\n"
            "    level: INFO\n"
            "  asyncio:\n"
            "    handlers: [console_worker]\n"
            "    propagate: yes\n"
            "    level: ERROR\n"
            "root:\n"
            "  handlers: [console_worker]\n"
            "  level: ERROR\n"
        )

        self.file_name = file_name()

        if "__pycache__" in __file__:
            # cached
            path_tests = Path(__file__).parent.parent
        else:
            # not cached
            path_tests = Path(__file__).parent

        self.path_cwd = path_tests.parent
        self.path_package_src = self.path_cwd.joinpath("src", g_app_name)

    def extract_yaml(self, str_fp: str, package_dest_c: str) -> Path:
        # extract worker conf
        path_dest = Path(str_fp).joinpath(package_dest_c, self.file_name)
        path_dest.parent.mkdir(mode=0o777, parents=True, exist_ok=True)
        path_dest.touch(mode=0o666, exist_ok=True)
        path_dest.write_text(self.yaml_worker)

        return path_dest

    def test_setup_logging_yaml(self):
        """defang then test"""
        with (
            tempfile.TemporaryDirectory() as fp,
            patch(  # use temp folder rather than user home data folder
                f"{g_app_name}.logging_yaml_abc._get_path_config",
                return_value=Path(fp),
            ),
            patch(  # defang
                "logging.config.dictConfig",
                return_value=True,
            ),
        ):
            # extract worker conf
            self.assertTrue(hasattr(self, "file_name"))
            self.assertIsInstance(self.file_name, str)
            self.assertNotEqual(len(self.file_name), 0)
            package_dest_c = "bar"
            path_yaml = self.extract_yaml(fp, package_dest_c)

            # Path or str
            valids = (
                path_yaml,
                self.yaml_worker,
            )
            func_path = f"{g_app_name}.logging_yaml_abc.setup_logging_yaml"
            kwargs = {}
            for arg0 in valids:
                t_ret = get_locals(func_path, setup_logging_yaml, *(arg0,), **kwargs)
                self.assertIsInstance(t_ret, tuple)
                ret, d_locals = t_ret
                self.assertIsInstance(d_locals["yaml_config"], s.YAML)
                self.assertIsInstance(d_locals["path_yaml"], type(arg0))
                #    Run w/o inspection
                setup_logging_yaml(arg0)

            # None or unsupported type. Does nothing
            invalids = (
                None,
                0.12345,
            )
            for invalid in invalids:
                setup_logging_yaml(invalid)

    def test_setup_public(self):
        """Setup worker by feeding it logging.config yaml"""
        with (
            tempfile.TemporaryDirectory() as fp,
            patch(  # defang
                "logging.config.dictConfig",
                return_value=True,
            ),
            patch(  # temp folder rather than :code:`$HOME/.local/share/[app]`
                f"{g_app_name}.logging_yaml_abc._get_path_config",
                return_value=Path(fp),
            ),
            patch(  # replace with mock
                f"{g_app_name}.logging_yaml_abc.setup_logging_yaml",
                return_value=True,
            ) as mock_setup,
        ):
            my_logger = MyLogger(
                self.g_package_second_party,
                partial(cb_joinpath, fp),
            )
            my_logger.setup(self.yaml_worker)
            mock_setup.assert_called_once()

            invalids = (
                None,
                0.12345,
            )
            for invalid in invalids:
                my_logger.setup(invalid)

    def test_as_str(self):
        """Read the yaml from file"""
        package_dest_c = "bar"
        with (
            tempfile.TemporaryDirectory() as fp,
            patch(  # temp folder rather than :code:`$HOME/.local/share/[app]`
                f"{g_app_name}.logging_yaml_abc._get_path_config",
                return_value=Path(fp).joinpath(package_dest_c),
            ),
        ):
            # Not extracted
            my_logger = MyLogger(
                package_dest_c,
                partial(cb_joinpath, fp),  # this gets ignored cuz overridden
            )
            with self.assertRaises(FileNotFoundError):
                str_yaml = my_logger.as_str()

            # extract valid yaml
            self.extract_yaml(fp, package_dest_c)
            #    no strictyaml.YAMLValidationError cuz valid

            # Mimic attempt to get file_stem without genre
            msg_exc = "Oh no!"
            with patch(
                f"{g_app_name}.logging_api_test.file_stem",
                side_effect=LoggingStrictGenreRequired(msg_exc),
            ):
                with self.assertRaises(LoggingStrictGenreRequired):
                    str_yaml = my_logger.as_str()

            str_yaml = my_logger.as_str()
            self.assertIsInstance(str_yaml, str)
            self.assertEqual(str_yaml, self.yaml_worker)

    def test_abc_register(self):
        """As long as class has these three methods can be registered as a DatumABC"""

        class AMockSpec:
            @property
            def file_stem(self) -> str:  # noqa: F811
                return "foobarbaz"

            @property
            def file_name(self) -> str:
                return "foobarbaz"

            @property
            def package(self) -> str:
                return "ur_package"

            @property
            def dest_folder(self) -> Path:
                return "ur_package"

            def extract(
                self,
                path_relative_package_dir: Path | str | None = "",
            ) -> str:
                pass

            def as_str(self) -> str:
                return "foobarbaz"

            def setup(self, str_yaml: str) -> None:
                pass

            def iter_yamls(
                self,
                path_dir: Path,
                category: Optional[str] = None,
                genre: Optional[str] = None,
                flavor: Optional[str] = None,
                version: Optional[str] = VERSION_FALLBACK,
            ) -> Iterator[Path]:
                pass

        """AMockSpec implements interface LoggingYamlType and is
        considered a subclass"""
        LoggingYamlType.register(AMockSpec)
        self.assertTrue(issubclass(AMockSpec, LoggingYamlType))

        props = (
            "file_stem",
            "file_name",
            "package",
            "dest_folder",
        )
        for prop_name in props:
            self.assertTrue(
                is_class_attrib_kind(
                    AMockSpec,
                    prop_name,
                    ClassAttribTypes.PROPERTY,
                ),
            )

        norm_meths = (
            "extract",
            "as_str",
            "setup",
            "iter_yamls",
        )
        for norm_meth in norm_meths:
            self.assertTrue(
                is_class_attrib_kind(
                    AMockSpec,
                    norm_meth,
                    ClassAttribTypes.METHOD,
                ),
            )

        # Is considered a subclass of LoggingYamlType?
        self.assertTrue(issubclass(AMockSpec, LoggingYamlType))
        LoggingYamlType.register(AMockSpec)

        class CMockSpec:
            def __str__(self):
                return "foobarbaz"

            def as_str(self):
                return "foobarbaz"

        # Is considered a subclass of LoggingYamlType?
        self.assertFalse(issubclass(CMockSpec, LoggingYamlType))
        self.assertFalse(issubclass(int, LoggingYamlType))

    def test_get_pattern(self):
        """pattern classmethod"""
        self.assertEqual(MyLogger.suffixes, ".my_logger")
        category = "app"
        genre = "textual"
        version_co = "1"
        flavor = "asz"

        suffix_cat_none = f".*{MyLogger.suffixes}"
        suffix_cat = f".{category}{MyLogger.suffixes}"
        # 1 means has a value, 0 means None, x unsupported type
        valids = (
            # 1, 1, 1, 1
            (
                (category,),
                {"genre": genre, "version": version_co, "flavor": flavor},
                f"{genre}_{version_co}_{flavor}",
                suffix_cat,
            ),
            # 1, 1, 1, 0
            (
                (category,),
                {"genre": genre, "version": version_co, "flavor": None},
                f"{genre}_{version_co}_*",
                suffix_cat,
            ),
            # 1, 1, 0, 0
            (
                (category,),
                {"genre": genre, "version": None, "flavor": None},
                f"{genre}_*_*",
                suffix_cat,
            ),
            # 1, 0, 0, 0
            (
                (category,),
                {"genre": None, "version": None, "flavor": None},
                "*_*_*",
                suffix_cat,
            ),
            # 0, 0, 0, 0
            # type[LoggingYamlType] constructor --> ValueError --> sys.exit(10)
            (
                (None,),
                {"genre": None, "version": None, "flavor": None},
                "*_*_*",
                suffix_cat_none,
            ),
            # 1, 1, x, 1 Can't have ** must be single *
            (
                (category,),
                {"genre": genre, "version": 0.12345, "flavor": flavor},
                f"{genre}_{VERSION_FALLBACK}_{flavor}",
                suffix_cat,
            ),
            # 1, 1, x, 0
            (
                (category,),
                {"genre": genre, "version": 0.12345, "flavor": None},
                f"{genre}_{VERSION_FALLBACK}_*",
                suffix_cat,
            ),
            # 1, 0, x, 0
            (
                (category,),
                {"genre": None, "version": 0.12345, "flavor": None},
                f"*_{VERSION_FALLBACK}_*",
                suffix_cat,
            ),
            # 0, 0, x, 0
            (
                (None,),
                {"genre": None, "version": 0.12345, "flavor": None},
                f"*_{VERSION_FALLBACK}_*",
                suffix_cat_none,
            ),
        )
        for t_args, kwargs, stem, suffix in valids:
            file_name = MyLogger.pattern(*t_args, **kwargs)
            self.assertEqual(file_name, f"{stem}{suffix}")

    def test_get_version(self):
        """get_version classmethod"""
        valids = (
            ("1", "1"),
            (1, "1"),
            (None, "*"),  # -> fallback version
            ("     ", VERSION_FALLBACK),  # is_not_ok -> fallback version
            (0.12345, VERSION_FALLBACK),  # is_not_ok -> fallback version
            ("22", "22"),  # there is nothing special about version = "1"
        )
        for val_in, expected in valids:
            str_out = LoggingYamlType.get_version(val_in)
            self.assertIsInstance(str_out, str)
            self.assertEqual(str_out, expected)


if __name__ == "__main__":  # pragma: no cover
    """Without coverage

    .. code-block:: shell

       python -m tests.test_abc --locals

       python -m unittest tests.test_abc \
       -k LoggingWorker.test_setup_logging_yaml --locals --verbose

       python -m unittest tests.test_abc \
       -k LoggingWorker.test_setup_public --locals --verbose

       python -m unittest tests.test_abc \
       -k LoggingWorker.test_as_str --locals --verbose

    With coverage

    .. code-block:: shell

       coverage run --data-file=".coverage-combine-41" \
       -m unittest discover -t. -s tests -p "test_abc*.py" --locals

       coverage run --data-file=".coverage-combine-33" \
       -m unittest discover -t. -s tests -p "test_logging_api*.py" --locals

       coverage combine --keep --data-file=".coverage-recipe-33-41" \
       .coverage-combine-33 .coverage-combine-41

       coverage report --include="**/logging_yaml_abc*" --no-skip-covered \
       --data-file=".coverage-recipe-33-41"

    """
    unittest.main(tb_locals=True)
