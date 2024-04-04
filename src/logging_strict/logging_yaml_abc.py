"""
.. moduleauthor:: Dave Faulkmore <faulkmore telegram>

Base class of logging_yaml implementations

:py:mod:`logging.config` yaml config files are exported to
:code:`$HOME/.locals/share/[app name]`

One for the app and another for worker(s).

``QA Tester`` can edit the yaml config files, **before using**,
ensure validation passes!

Module private variables
-------------------------

.. py:data:: __all__
   :type: tuple[str, str, str]
   :value: ("LoggingYamlType", "YAML_LOGGING_CONFIG_SUFFIX", "setup_logging_yaml")

   Module exports

.. py:data:: YAML_LOGGING_CONFIG_SUFFIX
   :type: str
   :value: ".logging.config.yaml"

   For logging.config YAML files, define file extension (Suffixes)
   Differentiates from other .yaml files

.. py:data:: VERSION_FALLBACK
   :type: str
   :value: "1"

   Initial version of :py:mod:`logging.config` YAML files

Module objects
---------------

"""

from __future__ import annotations

import abc
import glob
import logging.config
from pathlib import (
    Path,
    PurePath,
)
from typing import (
    TYPE_CHECKING,
    Any,
)

import strictyaml as s

from .exceptions import LoggingStrictGenreRequired
from .logging_yaml_validate import validate_yaml_dirty
from .util.check_type import (
    is_not_ok,
    is_ok,
)
from .util.xdg_folder import _get_path_config

__all__ = ("LoggingYamlType", "YAML_LOGGING_CONFIG_SUFFIX", "setup_logging_yaml")

YAML_LOGGING_CONFIG_SUFFIX = ".logging.config.yaml"
VERSION_FALLBACK = "1"


def setup_logging_yaml(path_yaml):
    """Loads :py:mod:`logging.config` configuration.

    Can pass in a path or a the YAML str

    :param path_yaml: :py:mod:`logging.config` YAML file path
    :type path_yaml: typing.Any

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


def as_str(package_name, file_name):
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
        """raises py:exc:`strictyaml.YAMLValidationError`
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
    def get_version(val):
        """Get a particular version of a :py:mod:`logging.config`
        yaml file

        :param val:

           To not filter, getting all versions, ``None``. To get
           the fallback version, pass in an unsupported type, e.g. 0.12345

        :type val: typing.Any
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
        category=None,
        genre=None,
        flavor=None,
        version=None,
    ):
        """Search pattern. Can't distinguish latest version.

        Each paramater narrows down search results.

        version applies to:

        - genre

        or

        - genre and flavor

        :param category:
        :type category: str | None
        :param genre:

           If UI: "textual" or "rich". If worker: "stream". Then can have
           a library of yaml files that can be used with a particular
           UI framework or worker type

        :type genre: str | None
        :param flavor:

           Unique identifier name given to a particular :py:mod:`logging.config`
           yaml. This name is slugified. Meaning period and underscores
           converted to hyphens

           Flavor is a very terse description, for a
           :paramref:`logging_strict.logging_yaml_abc.LoggingYamlType.pattern.params.genre`,
           how this yaml differs from others. If completely generic, call it
           ``generic``. If different handlers or formatters or filters are
           used, what is the yaml's purpose?

        :type flavor: str | None
        :param version:

           Default "1". Version of this particular
           :paramref:`logging_strict.logging_yaml_abc.LoggingYamlType.pattern.params.category`.
           **Not** the version of the yaml spec. Don't confuse the two.

        :type version: typing.Any | None
        :returns: Pattern used with :py:func:`glob.glob` to find files
        :rtype: str
        """
        # None --> fallback. Not able to know what is the latest version
        str_version = LoggingYamlType.get_version(version)

        if is_ok(category):
            file_suffixes = f".{category}{cls.suffixes}"
        else:
            """empty str, unsupported type, or None, or str with only
            whitespace would be stopped by
            type[logging_strict.logging_yaml_abc.LoggingYamlType]
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

    def iter_yamls(self, path_dir):
        """Conducts a recursive search thru the folder tree starting from
        package base data folder, further narrow search by relative
        (to package base data folder) path,
        :paramref:`logging_strict.logging_yaml_abc.LoggingYamlType.iter_yamls.params.path_dir`

        Iterator of absolute path of search results

        :param path_dir:

           Absolute path to a folder

        :type path_dir: pathlib.Path | None
        :returns: Within folder tree, iterator of yaml

           ``True`` if at least one yaml file exists in folder
           otherwise ``False``

        :rtype: collections.abc.Iterator[pathlib.Path]
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
    def __subclasshook__(cls, C):
        """A class wanting to be
        :py:class:`~logging_strict.logging_yaml_abc.LoggingYamlType`,
        minimally requires:

        Properties:

        - file_stem

        - file_name

        - package

        - dest_folder

        Methods:

        - extract

        - as_str -- get for free

        - setup -- get for free

        Then register itself
        :code:`LoggingYamlType.register(AnotherDatumClass)` or subclass
        :py:class:`~logging_strict.logging_yaml_abc.LoggingYamlType`

        :param C:

           Class to test whether implements this interface or is a subclass

        :type C: typing.Any
        :returns:

           ``True`` implements
           :py:class:`~logging_strict.logging_yaml_abc.LoggingYamlType`
           interface or is a subclass. ``False`` not a
           :py:class:`~logging_strict.logging_yaml_abc.LoggingYamlType`

        :rtype: bool
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
    def file_stem(self):
        """Get file stem

        :returns: file stem
        :rtype: str
        """
        ...

    @property
    @abc.abstractmethod
    def file_name(self):
        """Get full file name. Includes stem and suffixes

        :returns: file name
        :rtype: str
        """
        ...

    @property
    @abc.abstractmethod
    def package(self):
        """Get package name

        :returns: package name
        :rtype: str
        """
        ...

    @property
    @abc.abstractmethod
    def dest_folder(self):
        """:py:mod:`logging.config` yaml file export destination folder

        :returns:

           Destination folder. XDG user data dir, on linux,
           :code:`$HOME/.local/share/[app name]`

        :rtype: pathlib.Path
        """
        ...

    @abc.abstractmethod
    def extract(self, path_relative_package_dir=""):
        """Extract :py:mod:`logging.config` yaml files to xdg user data dir

        :param path_relative_package_dir:

           Default empty string. Relative to the package base data
           folder, provide a relative path or str to narrow search results

        :type path_relative_package_dir: pathlib.Path | str | None
        :returns:

           Destination path of extracted/exported :py:mod:`logging.config` yaml file(s)

        :rtype: str
        """
        ...

    def as_str(self):
        """Read the YAML config file, raise an error if not there or invalid

        The yaml files must have already been extracted from a package

        :returns: YAML str. Pass this to each worker
        :rtype: str
        :raises:

           - :py:exc:`strictyaml.exceptions.YAMLValidationError` -- Invalid.
             Validation against logging.config schema failed

           - :py:exc:`FileNotFoundError` -- Could not find logging config YAML file

           - :py:exc:`~logging_strict.exceptions.LoggingStrictGenreRequired` --
             Genre required to get file name

        """
        try:
            self.file_stem
        except LoggingStrictGenreRequired as e:
            msg_exc = "Without genre, cannot retrieve logging.config yaml file"
            raise LoggingStrictGenreRequired(msg_exc) from e

        ret = as_str(self.package, self.file_name)

        return ret

    def setup(self, str_yaml):  # pragma: no cover dangerous
        """Only called by app, not worker. For worker, is a 2 step
        process, not 1.

        A :py:class:`multiprocessing.pool.Pool` worker, needs
        to be feed the contents of the :py:mod:`logging.config`
        YAML file

        xdg user data folder: :code:`$HOME/.local/share/[app name]`

        :param str_yaml: :py:mod:`logging.config` yaml str
        :type str_yaml: str
        """
        if is_ok(str_yaml):
            setup_logging_yaml(str_yaml)
        else:  # pragma: no cover
            pass
