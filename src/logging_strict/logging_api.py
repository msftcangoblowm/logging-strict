"""
.. py:module:: logging_strict.logging_api
   :platform: Unix
   :synopsis: Extract and load logging.config

.. moduleauthor:: Dave Faulkmore <faulkmore telegram>

..

:py:mod:`logging` is thread-safe. A change in one thread affects every
thread. And logging config is dirty, each logger, since it's a Singleton,
stays around for the life of the app. So the app and workers need to be
isolated from each other. **ProcessPool > ThreadPool**. Workers should
exist as separate processes. The logging state ends along with the worker process.

Another design consideration is avoiding blocking the main app thread.
A message queue manager (rabbitmq) can mitigate this issue.

So there needs to be two categories of logging.config yaml files:

- app

Uses a (logging) handler specific for a particular UI framework

- worker

(logging) handler is directed at console or files. If log to console
(:py:class:`logging.handlers.StreamHandler`), capture the worker
logging output, including it along with the worker output.

Module private variables
-------------------------

.. py:data:: __all__
   :type: tuple[str, str, str, str, str]
   :value: ("LoggingConfigYaml", "setup_ui", \
   "worker_yaml_curated", "setup_worker_other", "LoggingState")

   Module exports


Module objects
---------------

"""
from __future__ import annotations

import sys
import threading
from functools import partial
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Optional,
)

import strictyaml as s

from .constants import (
    LoggingConfigCategory,
    g_app_name,
)
from .exceptions import (
    LoggingStrictGenreRequired,
    LoggingStrictPackageNameRequired,
    LoggingStrictPackageStartFolderNameRequired,
    LoggingStrictProcessCategoryRequired,
)
from .logging_yaml_abc import (
    VERSION_FALLBACK,
    YAML_LOGGING_CONFIG_SUFFIX,
    LoggingYamlType,
)
from .util.check_type import (
    is_not_ok,
    is_ok,
)
from .util.package_resource import (
    PackageResource,
    PartStem,
    PartSuffix,
    filter_by_file_stem,
    filter_by_suffix,
)
from .util.xdg_folder import _get_path_config

if sys.version_info >= (3, 8):  # pragma: no cover
    from collections.abc import Iterator
else:  # pragma: no cover
    from typing import Iterator

if sys.version_info >= (3, 9):  # pragma: no cover
    try:
        from importlib.resources.abc import Traversable  # py312+
    except ImportError:  # pragma: no cover
        from importlib.abc import Traversable  # py39+
else:  # pragma: no cover
    msg_exc = "Traversable py39+"
    raise ImportError(msg_exc)

__all__ = (
    "LoggingConfigYaml",
    "setup_ui",
    "worker_yaml_curated",
    "setup_worker_other",
    "LoggingState",
)


def cb_true(x):
    return True


class LoggingConfigYaml(LoggingYamlType):
    """For the UI, extract and setup :py:mod:`logging.config` yaml file

    A category is prefixed to the file suffixes. The final file suffixes becomes:

    - for the UI process

       :menuselection:`.logging.config.yaml --> .app.logging.config.yaml`.

    - for the worker process(es)

       :menuselection:`.logging.config.yaml --> `.worker.logging.config.yaml`

    :cvar suffixes:

       :py:mod:`logging.config` yaml file suffixes. A category is prefixed.
       So e.g. for the UI process, the final file suffixes becomes
       :menuselection:`.logging.config.yaml --> .app.logging.config.yaml`.
       For the worker the final suffixes would be `.worker.logging.config.yaml`

    :vartype suffixes: str
    :ivar package_name:

       The Python package containing the :py:mod:`logging.config` yaml
       file(s). Curating in one place, commonly used, yaml files is
       better than having copies in each and every Python package

    :vartype package_name: str
    :ivar category:

       LoggingConfigCategory.UI or LoggingConfigCategory.WORKER

       The logging configuration will not be the same for main process
       and for workers.

       The main process, even if headless is considered to be the UI. Heavy
       background processing occurs in workers. These are run in a separate process,
       not merely a thread. This design prevents :py:mod:`logging.config`
       changes from polluting other workers or the main process.

    :vartype category: :py:class:`LoggingConfigCategory`
    :ivar genre:

       If UI: "textual" or "rich". If worker: "stream". Then can have
       a library of yaml files that can be used with a particular
       UI framework or worker type

    :vartype genre: str or None
    :ivar flavor:

       Unique identifier name given to a particular :py:mod:`logging.config`
       yaml. This name is slugified. Meaning period and underscores
       converted to hyphens

       Flavor is a very terse description, for a :paramref:`genre`, how
       this yaml differs from others. If completely generic, call it
       ``generic``. If different handlers or formatters or filters are
       used, what is the yaml's purpose?

    :vartype flavor: str or None
    :ivar version_no:

       Default 1. Version of this particular
       :paramref:`logging_config_yaml_co`. **Not** the version of the
       yaml spec. Don't confuse the two.

    :vartype version_no: :py:class:`~typing.Any` or None
    :raises:

       - :py:exc:`LoggingStrictPackageNameRequired` -- Package name required for
         determining destination folder

       - :py:exc:`LoggingStrictPackageStartFolderNameRequired` -- Package base
         data folder name is required

    """

    suffixes: str = YAML_LOGGING_CONFIG_SUFFIX

    def __init__(
        self,
        package_name: str,
        package_data_folder_start: str,
        category: LoggingConfigCategory | str | Any | None,
        genre: Optional[str] = None,
        flavor: Optional[str] = None,
        version_no: Optional[Any] = VERSION_FALLBACK,
    ):
        super().__init__()

        if is_ok(package_name):
            self._package_name = package_name
        else:
            msg_exc = (
                "Package name required. Which package contains logging.config files?"
            )
            raise LoggingStrictPackageNameRequired(msg_exc)

        if is_ok(package_data_folder_start):
            self._package_data_folder_start = package_data_folder_start
        else:
            msg_exc = (
                f"Within package {package_name}, from the package base, "
                "the 1st folder, folder name is required"
            )
            raise LoggingStrictPackageStartFolderNameRequired(msg_exc)

        # LoggingConfigCategory.UI.value

        if is_ok(category) and category in LoggingConfigCategory.categories():
            self._category = category
        elif (
            category is not None
            and isinstance(category, LoggingConfigCategory)
            and category in LoggingConfigCategory
        ):
            self._category = category.value
        else:
            # iter_yaml ok. extract, as_str, setup not ok
            self._category = None

        """ Should slugify genre and flavor

        Intention is to curate common ``*.logging.config yaml`` files
        and include in this package"""
        if is_ok(genre):
            self._genre = genre
        else:
            # iter_yaml is ok. extract or setup is not
            self._genre = None

        if is_ok(flavor):
            self._flavor = flavor
        else:
            self._flavor = None

        self.version = version_no

    @property
    def file_stem(self) -> str:
        """file stem consists of slugs seperated by underscore

        :returns: File name. Which is file stem + suffixes
        :rtype: str
        :raises:

           - :py:exc:`LoggingStrictGenreRequired` --- Genre is required. e.g.
             textual pyside mp rabbitmq

        .. todo:: slugify

           The code and flavor should be only hyphens. Then separate
           these tokens with underscores

        """
        if is_not_ok(self.genre):
            msg_exc = "Provide which UI framework is being used"
            raise LoggingStrictGenreRequired(msg_exc)

        ret = f"{self.genre}_{self.version}"

        if self._flavor is not None:
            ret = f"{ret}_{self._flavor}"
        else:  # pragma: no cover
            pass

        return ret

    @property
    def category(self) -> str:
        return self._category

    @property
    def genre(self) -> Optional[str]:
        return self._genre

    @property
    def flavor(self) -> str:
        return self._flavor

    @property
    def version(self) -> str:
        return self._version

    @version.setter
    def version(self, val: Any) -> None:
        # version of the flavor or if no flavor then of the yaml file
        # parent abc staticmethod
        self._version = LoggingYamlType.get_version(val)

    @property
    def file_suffix(self) -> str:
        """Suffixes: ``.[category].logging.config yaml``"""
        if is_not_ok(self.category):
            msg_exc = (
                f"Unknown category, {self.category}. Choices: "
                f"{tuple(LoggingConfigCategory.categories())}"
            )
            raise LoggingStrictProcessCategoryRequired(msg_exc)
        else:  # pragma: no cover
            pass

        cls = type(self)
        ret = f".{self.category}{cls.suffixes}"

        return ret

    @property
    def file_name(self) -> str:
        try:
            ret = f"{self.file_stem}{self.file_suffix}"
        except LoggingStrictProcessCategoryRequired as e:
            msg_exc = (
                f"Unknown category {self.category}. Choices: "
                f"{tuple(LoggingConfigCategory.categories())}"
            )
            raise LoggingStrictProcessCategoryRequired(msg_exc) from e
        except LoggingStrictGenreRequired as e:
            msg_exc = "Cannot get the file name without genre"
            raise LoggingStrictGenreRequired(msg_exc) from e

        return ret

    @property
    def package(self) -> str:
        return self._package_name

    @property
    def dest_folder(self) -> Path:
        return _get_path_config(self.package)

    def extract(
        self,
        path_relative_package_dir: Path | str | None = "",
    ) -> str:
        """folder of yaml file is unknown, find the file

        :param path_relative_package_dir:

           Default empty string which means search the entire package.
           Specifying a start folder narrows the search

        :type path_relative_package_dir: :py:class:`~pathlib.Path` or str or None
        :returns: Relative path, within package, to ``*.*.logging.config.yaml``
        :rtype: str

        :raises:

           - :py:exc:`AssertionError` -- Expecting one yaml file, many found
           - :py:exc:`FileNotFoundError` -- No yaml files found

        """
        if TYPE_CHECKING:
            cb_suffix: PartSuffix
            cb_file_stem: PartStem
            gen: Iterator[Traversable]

        if is_ok(path_relative_package_dir):
            from_where = f"{path_relative_package_dir} folder"
        else:
            from_where = "base folder"

        # To extract, genre required
        try:
            self.file_stem
        except LoggingStrictGenreRequired:
            # Will result in too broad of a search
            cb_file_stem = cb_true
            file_stem = None
        else:
            cb_file_stem = partial(filter_by_file_stem, self.file_stem)
            file_stem = self.file_stem

        try:
            self.file_suffix
        except LoggingStrictProcessCategoryRequired:
            cb_suffix = cb_true
            file_name = "??.??" if file_stem is None else f"{file_stem}.??"
        else:
            cb_suffix = partial(filter_by_suffix, self.file_suffix)
            file_suffix = self.file_suffix
            file_name = f"??.{file_suffix}" if file_stem is None else self.file_name

        pr = PackageResource(self.package, self._package_data_folder_start)

        gen = pr.package_data_folders(
            cb_suffix=cb_suffix,
            cb_file_stem=cb_file_stem,
            path_relative_package_dir=path_relative_package_dir,
        )
        folders = list(gen)
        folder_count = len(folders)
        if folder_count > 1:
            msg_err = (
                f"Within package {self.package}, starting from "
                f"{from_where}, found {str(folder_count)} "
                f"{file_name}. Expected one. Adjust / narrow "
                "param, path_relative_package_dir"
            )
            raise AssertionError(msg_err)
        elif folder_count == 0:
            msg_err = (
                f"Within package {self.package}, starting from "
                f"{from_where}, found {str(folder_count)} "
                f"{file_name}. Expected one. Is in this package? "
                "Is folder too specific? Try casting a wider net?"
            )
            raise FileNotFoundError(msg_err)
        else:  # pragma: no cover
            pass
        gen = pr.package_data_folders(
            cb_suffix=cb_suffix,
            cb_file_stem=cb_file_stem,
            path_relative_package_dir=path_relative_package_dir,
        )
        path_ret = next(
            pr.resource_extract(
                gen,
                self.dest_folder,
                cb_suffix=cb_suffix,
                cb_file_stem=cb_file_stem,
                is_overwrite=False,
                as_user=True,
            )
        )
        str_ret = str(path_ret.relative_to(self.dest_folder))

        return str_ret


def setup_ui(
    package_name: str,
    package_data_folder_start: str,
    genre: str,
    flavor: str,
    version_no: Optional[Any] = "1",
    package_start_relative_folder="",
) -> None:
    """Before creating an App instance, extract logging.config yaml
    for app, but not workers"""
    try:
        ui_yaml = LoggingConfigYaml(
            package_name,
            package_data_folder_start,
            LoggingConfigCategory.UI,
            genre=genre,
            flavor=flavor,
            version_no=version_no,
        )
    except (
        LoggingStrictPackageNameRequired,
        LoggingStrictPackageStartFolderNameRequired,
    ):
        raise

    # extract and validate
    try:
        ui_yaml.extract(path_relative_package_dir=package_start_relative_folder)
        str_yaml = ui_yaml.as_str()
    except (FileNotFoundError, s.YAMLValidationError, AssertionError):
        raise

    # LoggingConfigYaml.setup is a wrapper of setup_logging_yaml
    # Checks: is_ok
    ui_yaml.setup(str_yaml)


def worker_yaml_curated(
    genre: Optional[Any] = "mp",
    flavor: Optional[Any] = "asz",
    version_no: Optional[Any] = "1",
    package_start_relative_folder="",
) -> str:
    """For multiprocessing workers, retrieve the yaml in this order:

    - xdg user data dir folder

    - logging_strict package

    If QA tester, modifies the exported logging.config yaml, those
    changes are not overwritten

    Process 2nd step is calling:
    :py:func:`logging_strict.logging_yaml_abc.setup_logging_yaml`

    :param genre:

       Default "mp". If UI: "textual" or "rich". If worker: "mp". Then can have
       a library of yaml files that can be used with a particular
       UI framework or worker type

    :type genre: str or None
    :param flavor:

       Default "asz". Unique identifier name given to a particular
       :py:mod:`logging.config` yaml. Should be one word w/o special characters

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
    :param package_start_relative_folder:

       Default empty string which means search the entire package.
       Further narrows down search, so as to differentiate between folders
       which contain file with the same file name

    :type package_start_relative_folder: :py:class:`~pathlib.Path` or str or None
    :returns: yaml file contents
    :rtype: str
    :raises:

       - :py:exc:`FileNotFoundError` -- yaml file not found within package

       - :py:exc:`strictyaml.exceptions.YAMLValidationError` -- yaml file
         validation failed

       - :py:exc:`AssertionError` -- Expecting one yaml file, many found


    """
    package_name = g_app_name
    package_data_folder_start = "configs"

    ui_yaml = LoggingConfigYaml(
        package_name,
        package_data_folder_start,
        LoggingConfigCategory.WORKER,
        genre=genre,
        flavor=flavor,
        version_no=version_no,
    )

    try:
        ui_yaml.extract(path_relative_package_dir=package_start_relative_folder)
        str_yaml = ui_yaml.as_str()
    except (FileNotFoundError, s.YAMLValidationError, AssertionError):
        raise

    return str_yaml


def setup_worker_other(
    package_name: str,
    package_data_folder_start: str,
    genre: str,
    flavor: str,
    version_no: Optional[Any] = "1",
    package_start_relative_folder="",
) -> str:
    """worker_yaml_curated grabs the logging.config yaml from logging-strict.
    Use this if located in another package

    Process 2nd step is calling:
    :py:func:`logging_strict.logging_yaml_abc.setup_logging_yaml`

    :param package_name:

       If logging_strict, use method worker_yaml_curated instead. Otherwise
       package name which contains the logging.config yaml files

    :type package_name: str
    :param package_data_folder_start:

       Within :paramref:`package_name`, base data folder name. Not a
       relative path. Does not assume ``data``

    :type package_data_folder_start: str
    :param genre:

       Default "mp". If UI: "textual" or "rich". If worker: "mp". Then can have
       a library of yaml files that can be used with a particular
       UI framework or worker type

    :type genre: str
    :param flavor:

       Default "asz". Unique identifier name given to a particular
       :py:mod:`logging.config` yaml. Should be one word w/o special characters

       Flavor is a very terse description, for a :paramref:`genre`, how
       this yaml differs from others. If completely generic, call it
       ``generic``. If different handlers or formatters or filters are
       used, what is the yaml's purpose?

    :type flavor: str
    :param version_no:

       Default 1. Version of this particular
       :paramref:`logging_config_yaml_co`. **Not** the version of the
       yaml spec. Don't confuse the two.

    :type version_no: :py:class:`~typing.Any` or None
    :param package_start_relative_folder:

       Default empty string which means search the entire package.
       Further narrows down search, so as to differentiate between folders
       which contain file with the same file name

    :type package_start_relative_folder: :py:class:`~pathlib.Path` or str or None
    :returns: yaml file contents
    :rtype: str
    :raises:

       - :py:exc:`FileNotFoundError` -- yaml file not found within package

       - :py:exc:`strictyaml.exceptions.YAMLValidationError` -- yaml file
         validation failed

       - :py:exc:`AssertionError` -- Expecting one yaml file, many found

       - :py:exc:`LoggingStrictPackageNameRequired` -- Which package
         are the logging.config yaml in?

       - :py:exc:`LoggingStrictPackageStartFolderNameRequired` -- Within the
         provided package, the package base data folder name

    """
    try:
        ui_yaml = LoggingConfigYaml(
            package_name,
            package_data_folder_start,
            LoggingConfigCategory.WORKER,
            genre=genre,
            flavor=flavor,
            version_no=version_no,
        )
    except (
        LoggingStrictPackageNameRequired,
        LoggingStrictPackageStartFolderNameRequired,
    ):
        raise

    try:
        ui_yaml.extract(path_relative_package_dir=package_start_relative_folder)
        str_yaml = ui_yaml.as_str()
    except (FileNotFoundError, s.YAMLValidationError, AssertionError):
        raise

    return str_yaml


class LoggingState:
    """Singleton to hold the current logging state.
    To know whether or not, run by app or from cli

    If run from app, logging is redirected to :py:class:`textual.logging.TextualHandler`
    If run from cli, logging is redirected to :py:class:`logging.handlers.StreamHandler`

    Knowing the logging mode (or state), first step towards restoring logging mode

    :param is_state_app:

       Default ``False``. Set to ``True`` if called by App. Set to
       ``False`` if called by cli

    :type is_state_app: :py:class:`~typing.Any` or ``None``
    :returns: Singleton pattern, so always same instance
    :rtype: LoggingState

    .. seealso::

       Thread safe Singleton
       https://medium.com/analytics-vidhya/how-to-create-a-thread-safe-singleton-class-in-python-822e1170a7f6

    """

    _instance: Optional["LoggingState"] = None
    _lock = threading.RLock()
    # __state: Optional[bool] = None

    def __new__(cls) -> "LoggingState":
        if cls._instance is None:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                else:  # pragma: no cover
                    pass
        else:  # pragma: no cover
            pass

        return cls._instance

    @classmethod
    def reset(cls) -> None:
        if cls._instance is not None:
            with cls._lock:
                if cls._instance:
                    cls._instance = None
                else:  # pragma: no cover
                    pass
        else:  # pragma: no cover
            pass

    @property
    def is_state_app(self) -> Optional[bool]:
        """Get logging state

        :returns: ``True`` if app logging state otherwise ``False`` cli logging state
        :rtype: bool
        """
        cls = type(self)
        with cls._lock:
            if hasattr(self, "_state"):
                ret = self._state
            else:
                ret = None

        return ret

    @is_state_app.setter
    def is_state_app(self, is_state_app: Any) -> None:
        """Would only ever be changed within a unittest or module dealing with logging

        - ``True`` app logging state

        - ``False`` cli_logging state

        If not a bool, logging state is not changed

        :param is_state_app: New logging state. ``True`` if app otherwise ``False``
        :type is_state_app: :py:class:`~typing.Any`
        """
        cls = type(self)
        with cls._lock:
            is_param_ok = is_state_app is not None and isinstance(is_state_app, bool)
            if is_param_ok:
                self._state = is_state_app
            else:
                pass
