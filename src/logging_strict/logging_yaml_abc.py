"""
.. py:module:: logging_strict.logging_yaml_abc
   :platform: Unix
   :synopsis: Refresh or reload logging state of worker

.. moduleauthor:: Dave Faulkmore <faulkmore telegram>

..

Module private variables
-------------------------

.. py:data:: __all__
   :type: tuple[str, str]
   :value: ("LoggingYamlType", "YAML_LOGGING_CONFIG_SUFFIX")

   Module exports

.. py:data:: YAML_LOGGING_CONFIG_SUFFIX
   :type: str
   :value: ".logging.config.yaml"

   For logging.config YAML files, define file extension (Suffixes)
   Differentiates from other .yaml files


Module objects
---------------

"""
from __future__ import annotations

import abc
import glob
import logging.config
import sys
from pathlib import (
    Path,
    PurePath,
)
from typing import (
    TYPE_CHECKING,
    Any,
    Optional,
)

import strictyaml as s

from .exceptions import LoggingStrictGenreRequired
from .logging_yaml_validate import validate_yaml_dirty
from .util.check_type import (
    is_not_ok,
    is_ok,
)
from .util.xdg_folder import _get_path_config

if sys.version_info >= (3, 9):  # pragma: no cover
    from collections.abc import Iterator
else:  # pragma: no cover
    from typing import Iterator

__all__ = ("LoggingYamlType", "YAML_LOGGING_CONFIG_SUFFIX", "setup_logging_yaml")

YAML_LOGGING_CONFIG_SUFFIX = ".logging.config.yaml"
VERSION_FALLBACK = "1"


def setup_logging_yaml(path_yaml: Any) -> None:
    """Loads :py:mod:`logging.config` configuration.
    yaml config files are exported into :code:`$HOME/.config/[app name]`.

    One for the app and another for workers.

    :param path_yaml: :py:class:`logging.config` YAML
    :type path_yaml: :py:class:`~pathlib.Path`

    ``QA Tester`` can edit the yaml config files, **but first** be sure to test them!

    :raises:

       - :py:exc:`strictyaml.YAMLValidationError` -- Invalid.
             Validation against logging.config schema failed

    """
    if TYPE_CHECKING:
        yaml_config: s.YAML
        d_config: dict[str, Any]

    if path_yaml is None:
        str_yaml = None
    else:
        if (
            issubclass(type(path_yaml), PurePath)
            and path_yaml.exists()
            and path_yaml.is_file()
        ):
            str_yaml = path_yaml.read_text()
        elif isinstance(path_yaml, str):
            # Provide the text rather than a file
            str_yaml = path_yaml
        else:
            # unsupported type
            str_yaml = None

    if is_ok(str_yaml):
        yaml_config = validate_yaml_dirty(str_yaml)
        # QA Tester is responsible to test the logging.config yaml file
        # A broken yaml config file will crash the app here
        d_config = yaml_config.data
        logging.config.dictConfig(d_config)  # test: defang
    else:  # pragma: no cover
        pass

    # During testing, return needed to get locals
    return None


def as_str(package_name: str, file_name: str) -> str:
    """Assumes package data file already extracted to expected folder

    :param package_name:

       Package that contained the :py:mod:`logging.config` yaml file.
       For determining folder path

    :type package_name: str
    :param file_name: File name of :py:mod:`logging.config` yaml file
    :type file_name: str
    :returns: Reads and validates yaml against the :py:mod:`logging.config` schema.
    :rtype: str

    :raises:

       - :py:exc:`strictyaml.YAMLValidationError` -- Invalid.
         Validation against logging.config schema failed

       - :py:exc:`FileNotFoundError` -- Could not find logging config YAML file

    """
    path_xdg_user_data_dir = _get_path_config(package_name)
    path_yaml = path_xdg_user_data_dir.joinpath(file_name)

    msg_err = (
        "Did not find a logging config YAML file. It's extracted "
        f"during app start. Expected location {str(path_yaml)}"
    )

    is_exists = path_yaml.exists() and path_yaml.is_file()
    if is_exists:
        # test load the yaml file
        str_yaml = path_yaml.read_text()
        """raises :py:exc:`strictyaml.YAMLValidationError`
        If another yaml implementation, the exception raised will
        be that implementation specific
        """
        yaml_config = validate_yaml_dirty(str_yaml)
        assert isinstance(yaml_config, s.YAML)
    else:
        raise FileNotFoundError(msg_err)

    return str_yaml


class LoggingYamlType(abc.ABC):
    """ABC for LoggingYaml implementations"""

    @staticmethod
    def get_version(val: Any) -> str:
        """Get a particular version of a :p:mod:`logging.config`
        yaml file

        :param val:

           To not filter, getting all versions, ``None``. To get
           the fallback version, pass in an unsupported type, e.g. 0.12345

        :type val: :py:class:`~typing.Any`
        :returns: version as a str (unsigned integer)
        :rtype: str
        """
        if val is not None:
            if isinstance(val, int) and val > 0:
                ret = str(val)
            elif is_ok(val):
                ret = val
            else:
                ret = VERSION_FALLBACK
        else:
            ret = "*"

        return ret

    @classmethod
    def pattern(
        cls,
        category: Optional[str] = None,
        genre: Optional[str] = None,
        flavor: Optional[str] = None,
        version: Optional[str] = None,
    ) -> str:
        """Search pattern. Can't distinguish latest version.

        If folder contains only one app and one worker
        :py:mod:`logging.config` yaml file then it's enough to
        specify only the category

        Same applies to genre, flavor, and version.

        """
        # None --> fallback. Not able to know what is the latest version
        str_version = LoggingYamlType.get_version(version)

        if is_ok(category):
            file_suffixes = f".{category}{cls.suffixes}"
        else:
            """empty str, unsupported type, or None, or str with only
            whitespace would be stopped by type[LoggingYamlType]
            constructor producing a ValueError
            """
            file_suffixes = f".*{cls.suffixes}"

        if is_not_ok(genre):
            if is_not_ok(flavor):
                file_stem = f"*_{str_version}_*"
            else:
                file_stem = f"*_{str_version}_{flavor}"
        else:
            if is_not_ok(flavor):
                file_stem = f"{genre}_{str_version}_*"
            else:
                file_stem = f"{genre}_{str_version}_{flavor}"

        ret = f"{file_stem}{file_suffixes}"

        return ret

    def iter_yamls(
        self,
        path_dir: Path,
    ) -> Iterator[Path]:
        """Conducts a recursive search thru the folder tree starting from
        :paramref:`path_dir`. Searchs for files matching :paramref:`pattern`

        Iterator of absolute path to yaml files

        :param path_dir:

           Absolute path to a folder

        :type path_dir: :py:class:`~pathlib.Path` or None
        :param category:

           LoggingConfigCategory.UI or LoggingConfigCategory.WORKER

           The logging configuration will not be the same for main process
           and for workers.

           The main process, even if headless is considered to be the UI. Heavy
           background processing occurs in workers. These are run in a separate process,
           not merely a thread. This design prevents :py:mod:`logging.config`
           changes from polluting other workers or the main process.

        :type category: :py:class:`LoggingConfigCategory`
        :param genre:

           If UI: "textual" or "rich". If worker: "stream". Then can have
           a library of yaml files that can be used with a particular
           UI framework or worker type

        :type genre: str
        :param flavor:

           Unique identifier name given to a particular :py:mod:`logging.config`
           yaml. This name is slugified. Meaning period and underscores
           converted to hyphens

           Flavor is a very terse description, for a :paramref:`genre`, how
           this yaml differs from others. If completely generic, call it
           ``generic``. If different handlers or formatters or filters are
           used, what is the yaml's purpose?

        :type flavor: str or None
        :param version_no:

           Default 1. Version of this particular
           :paramref:`logging_config_yaml_co`. **Not** the version of the
           yaml spec. Don't confuse the two.

        :type version_no: :py:class:`~typing.Any` or None
        :returns: Within folder tree, iterator of yaml

           ``True`` if at least one yaml file exists in folder
           otherwise ``False``

        :rtype: Iterator[Path]
        """
        cls = type(self)
        # print(f"{self.category} {self.genre} {self.flavor} {self.version}")
        pattern = cls.pattern(
            category=self.category,
            genre=self.genre,
            flavor=self.flavor,
            version=self.version,
        )
        if path_dir is None or (
            path_dir is not None and not issubclass(type(path_dir), PurePath)
        ):
            # Path not provided
            yield from ()
        else:
            if not path_dir.exists() or not path_dir.is_dir():
                yield from ()
            else:
                # py310+ --> kw param root_dir
                search_query = f"{path_dir}/**/{pattern}"
                # print(f"search_query: {search_query}", file=sys.stderr)
                for path_yaml in glob.glob(
                    search_query,
                    # root_dir=path_dir, py310
                    recursive=True,
                ):
                    yield Path(path_yaml)

    @classmethod
    def __subclasshook__(cls, C: Any) -> bool:
        """A class wanting to be LoggingYamlType, requires minimally these methods:

        - as_rich
        - as_str
        - __str__

        Then register itself
        LoggingYamlType.register(AnotherDatumClass) or subclass :py:class:`LoggingYamlType`
        """
        if cls is LoggingYamlType:
            methods = (
                "file_stem",
                "file_name",
                "package",
                "dest_folder",
                "extract",
                "as_str",
                "setup",
            )

            expected_count = len(methods)
            for B in C.__mro__:
                lst = [True for meth in methods if meth in B.__dict__]
                match_count = len(lst)
                is_same = match_count == expected_count
                if is_same:
                    return True
        else:  # pragma: no cover
            pass
        return NotImplemented  # pragma: no cover Tried long enough with issubclass

    @property
    @abc.abstractmethod
    def file_stem(self) -> str:
        ...

    @property
    @abc.abstractmethod
    def file_name(self) -> str:
        ...

    @property
    @abc.abstractmethod
    def package(self) -> str:
        ...

    @property
    @abc.abstractmethod
    def dest_folder(self) -> Path:
        ...

    @abc.abstractmethod
    def extract(
        self,
        path_relative_package_dir: Path | str | None = "",
    ) -> str:
        ...

    def as_str(self) -> str:
        """Read the YAML config file, raise an error if not there or invalid

        The yaml files must have already been extracted from a package

        :returns: YAML str. Pass this to each worker
        :rtype: str
        :raises:

           - :py:exc:`strictyaml.YAMLValidationError` -- Invalid.
             Validation against logging.config schema failed

           - :py:exc:`FileNotFoundError` -- Could not find logging config YAML file

           - :py:exc:`LoggingStrictGenreRequired` -- Genre required to get file name

        """
        try:
            self.file_stem
        except LoggingStrictGenreRequired as e:
            msg_exc = "Without genre, cannot retrieve logging.config yaml file"
            raise LoggingStrictGenreRequired(msg_exc) from e

        ret = as_str(self.package, self.file_name)

        return ret

    def setup(self, str_yaml: str) -> None:  # pragma: no cover dangerous
        """A multiprocessing ProcessPool worker, needs to be
        feed the :py:mod:`logging.config` YAML file

        xdg user data folder: :code:`$HOME/.local/share/[app name]`

        During testing call LoggingConfigYaml.extract()

        Only called by app, not worker. For worker, is a 2 step process, not 1.

        :param str_yaml: logging.config yaml str
        :type str_yaml: str
        """
        if is_ok(str_yaml):
            setup_logging_yaml(str_yaml)
        else:  # pragma: no cover
            pass
