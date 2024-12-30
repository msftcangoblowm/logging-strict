"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

..

:py:mod:`logging` is thread-safe. A change in one thread affects every
thread. And logging config is dirty, each logger, since it's a Singleton,
stays around for the life of the app. So the app and workers need to be
isolated from each other.

:py:class:`multiprocessing.pool.Pool` > ThreadPool. Workers should
exist as separate processes. The logging state ends along with the worker process.

Another design consideration is avoiding blocking the main app thread.
A message queue manager (rabbitmq) can mitigate this issue.

So there needs to be two categories of logging.config yaml files:

- app

Uses a (logging) handler specific for a particular UI framework

- worker

(logging) handler is directed at console or files. If log to console
(:py:class:`logging.StreamHandler`), capture the worker
logging output, including it along with the worker output.

**Module private variables**


.. py:data:: __all__
   :type: tuple[str, str, str, str, str, str]
   :value: ("LoggingConfigYaml", "setup_ui_other", "ui_yaml_curated", \
   "worker_yaml_curated", "setup_worker_other", "LoggingState")

   Module exports


**Module objects**


"""

from __future__ import annotations

import sys
import threading
from functools import partial
from typing import TYPE_CHECKING

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
    after_as_str_update_package_name,
)
from .util.check_type import (
    is_not_ok,
    is_ok,
)
from .util.package_resource import (
    PackageResource,
    PartStem,
    PartSuffix,
    _to_package_case,
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
    "ui_yaml_curated",
    "setup_ui_other",
    "worker_yaml_curated",
    "setup_worker_other",
    "LoggingState",
)


def cb_true(x):
    """A Callback which always returns ``True``

    Used to retrieve files with either all file stem or all file suffixes

    :returns: Always ``True``
    :rtype: bool
    """
    return True


class LoggingConfigYaml(LoggingYamlType):
    """For the UI, extract and setup :py:mod:`logging.config` yaml file

    A category is prefixed to the file suffixes. The final file suffixes becomes:

    - for the UI process

       :menuselection:`.logging.config.yaml --> .app.logging.config.yaml`.

    - for the worker process(es)

       :menuselection:`.logging.config.yaml --> `.worker.logging.config.yaml`

    Class variables

    :cvar suffixes:

       .. line-block::

          :py:mod:`logging.config` yaml file suffixes

          value: ``.logging.config.yaml``

          A category will be prefix'ed.

          For the UI process, the final file suffixes becomes
          :menuselection:`.logging.config.yaml --> .app.logging.config.yaml`.

          For the worker, the final suffixes would becomes
          :menuselection:`.logging.config.yaml --> .worker.logging.config.yaml`


    :vartype suffixes: str

    Instance variables

    :ivar package_name:

       The Python package containing the :py:mod:`logging.config` yaml
       file(s). Curating in one place, commonly used, yaml files is
       better than having copies in each and every Python package

    :vartype package_name: str
    :ivar package_data_folder_start: relative path, within package, to data folder
    :vartype package_data_folder_start: str
    :ivar category:

       LoggingConfigCategory.UI or LoggingConfigCategory.WORKER

       The logging configuration will not be the same for main process
       and for workers.

       The main process, even if headless is considered to be the UI. Heavy
       background processing occurs in workers. These are run in a separate process,
       not merely a thread. This design prevents :py:mod:`logging.config`
       changes from polluting other workers or the main process.

    :vartype category:

       logging_strict.constants.LoggingConfigCategory | str | typing.Any | None

    :ivar genre:

       If UI: "textual" or "rich". If worker: "stream". Then can have
       a library of yaml files that can be used with a particular
       UI framework or worker type

    :vartype genre: str | None
    :ivar flavor:

       Unique identifier name given to a particular :py:mod:`logging.config`
       yaml. This name is slugified. Meaning period and underscores
       converted to hyphens

       Flavor is a very terse description, for a
       :py:obj:`LoggingConfigYaml.genre <logging_strict.logging_api.LoggingConfigYaml.genre>`,
       how this yaml differs from others. If completely generic, call it
       ``generic``. If different handlers or formatters or filters are
       used, what is the yaml's purpose?

    :vartype flavor: str | None
    :ivar version_no:

       .. line-block::

          Default 1. Version of this particular
          genre or genre & flavor

          **Not** the version of the yaml spec. Don't confuse the two.

    :vartype version_no: typing.Any | None
    :raises:

       - :py:exc:`logging_strict.exceptions.LoggingStrictPackageNameRequired`
         -- Package name required for determining destination folder

       - :py:exc:`logging_strict.exceptions.LoggingStrictPackageStartFolderNameRequired`
         -- Package base data folder name is required

    """

    suffixes: str = YAML_LOGGING_CONFIG_SUFFIX

    def __init__(
        self,
        package_name,
        package_data_folder_start,
        category,
        genre=None,
        flavor=None,
        version_no=VERSION_FALLBACK,
    ):
        """Class constructor"""
        super().__init__()

        # may raise LoggingStrictPackageNameRequired
        self.package = package_name

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
    def file_stem(self):
        """file stem consists of slugs seperated by underscore

        :returns: File name. Which is file stem + suffixes
        :rtype: str
        :raises:

           - :py:exc:`logging_strict.exceptions.LoggingStrictGenreRequired`
             -- Genre is required. e.g. textual pyside mp rabbitmq

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
    def category(self):
        """Category as a str. Category str either: 'app' or 'worker'

        :returns: Category str
        :rtype: str
        """
        return self._category

    @property
    def genre(self):
        """In constructor can neglect to provide genre.

        So can use:

        - :py:meth:`LoggingYamlType.iter_yamls <logging_strict.logging_yaml_abc.LoggingYamlType.iter_yamls>`

        Can't use

        - :py:meth:`LoggingConfigYaml.extract <logging_strict.logging_api.LoggingConfigYaml.extract>`

        - :py:meth:`LoggingYamlType.setup <logging_strict.logging_yaml_abc.LoggingYamlType.setup>`

        Genre is the UI framwork or worker characteristic

        - imply the handler. e.g. textual or rich

        - imply the characteristics of a worker :abbr:`ep (entrypoint)`.
          e.g. :abbr:`mp (multiprocessing)` or :abbr:`mq (rabbitmq)`

        :returns: Genre str
        :rtype: str | None
        """
        return self._genre

    @property
    def flavor(self):
        """Specific implementation of a genre.

        E.g. multiple :py:mod:`logging.config` yaml files for
        :py:mod:`textual`

        Uses the handler,
        :py:exc:`textual.logging.TextualHandler`, but each
        has some variation. Like custom formaters or filters

        So the flavor may be

        - Package that originally uses it and provided it to be curated
          within logging_strict e.g. :abbr:`asz (testing console UI)`

        - One word, no hyphen period or underscore, description of the
          uniqueness of this variation

        :returns: Flavor str
        :rtype: str | None
        """
        return self._flavor

    @property
    def version(self):
        """Applies to the genre or genre & flavor.

        Default "1"

        Do not confuse with yaml spec version

        :returns: :py:mod:`logging.config` yaml file version
        :rtype: str
        """
        return self._version

    @version.setter
    def version(self, val):
        """Version setter

        :param val: Default "1". May be an int or str
        :type val: typing.Any
        """
        self._version = LoggingYamlType.get_version(val)

    @property
    def file_suffix(self):
        """Suffixes: ``.[category].logging.config yaml``

        :returns: file suffixes
        :rtype: str
        :raises:

           - :py:exc:`logging_strict.exceptions.LoggingStrictProcessCategoryRequired`
             -- Requires category

        """
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
    def file_name(self):
        """Get the file name. Can raise exceptions if category and/or
        genre were not provided to the constructor

        :returns: file name
        :rtype: str
        :raises:

           - :py:exc:`logging_strict.exceptions.LoggingStrictProcessCategoryRequired`
             -- Category required

           - :py:exc:`logging_strict.exceptions.LoggingStrictGenreRequired`
             -- Genre required

        """
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
    def package(self):
        """Package name (underscores, not hyphens) where the
        :py:mod:`logging.config` yaml file is located.

        Ideally should be curated in |project_name|

        :returns: Package name
        :rtype: str
        """
        return self._package_name

    @package.setter
    def package(self, val):
        """Package name is supposed to be a dotted path.
        Apply :py:func:`logging_strict.util.package_resource._to_package_case`

        :param val: package name must be a dotted path
        :type val: typing.Any

        :raises:

           - :py:exc:`LoggingStrictPackageNameRequired` -- Package name
             required for determining destination folder

        """
        if is_ok(val):
            """Expects a valid package name; a dotted path. Coerse into
            a dotted path.

            e.g. logging-strict --> logging_strict

            Understandable mistake. Very hard to spot. Nearly correct.
            """
            self._package_name = _to_package_case(val)
        else:
            msg_exc = (
                "Package name required. Which package contains logging.config files?"
            )
            raise LoggingStrictPackageNameRequired(msg_exc)

    @property
    def dest_folder(self):
        """Normally xdg user data dir. During testing, temp folder used instead

        :returns: Destination folder
        :rtype: pathlib.Path
        """
        return _get_path_config(self.package)

    def extract(self, path_relative_package_dir=""):
        """folder of yaml file is unknown, find the file

        :param path_relative_package_dir:

           Default empty string which means search the entire package.
           Specifying a start folder narrows the search

        :type path_relative_package_dir: pathlib.Path | str | None
        :returns: Relative path, within package, to ``*.*.logging.config.yaml``
        :rtype: str

        :raises:

           - :py:exc:`ImportError` -- Cannot extract files. Install package then try again
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

        package_name_dotted_path = self.package
        pr = PackageResource(package_name_dotted_path, self._package_data_folder_start)

        try:
            gen = pr.package_data_folders(
                cb_suffix=cb_suffix,
                cb_file_stem=cb_file_stem,
                path_relative_package_dir=path_relative_package_dir,
            )
            folders = list(gen)
        except ImportError as exc:
            msg_err = (
                f"package {self.package} is not installed in venv. "
                "Cannot extract files. Install package then try again"
            )
            raise ImportError(msg_err) from exc

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


def setup_ui_other(
    package_name,
    package_data_folder_start,
    genre,
    flavor,
    version_no=VERSION_FALLBACK,
    package_start_relative_folder="",
    logger_package_name=None,
) -> None:
    """Before creating an App instance, seemlessly extracts
    :py:mod:`logging.config` yaml file for app, but not worker(s)

    :param package_name: Package name containing :py:mod:`logging.config` yaml file
    :type package_name: str
    :param package_data_folder_start:

       Package base data folder name. Not a relative path. This is the
       fallback search folder. Use package_start_relative_folder to
       further narrow the search

    :type package_data_folder_start: str
    :param genre:

       UI framework or worker implementation characteristic.
       E.g. textual, rich, :abbr:`mp (multiprocessing)`, or :abbr:`mq (rabbitmq)`

    :type genre: str
    :param flavor:

       Brand or how variation differs. e.g. :abbr:`asz (testing console UI)`

    :type flavor: str
    :param version_no: Default "1". Applies to genre or genre & flavor
    :type version_no: typing.Any | None
    :param package_start_relative_folder:

       .. line-block::

          Default empty string.

          Relative to package_data_folder_start.
          Relative path to further narrow down which folder contains the
          :py:mod:`logging.config` yaml file.

          Needed when multiple folders contain :py:mod:`logging.config` yaml file
          with same file name


    :type package_start_relative_folder: str | None
    :param logger_package_name:

       Default None. Update the dict to set a more appropriate logger package name.
       Will always want to do this

    :type logger_package_name: str | None
    :raises:

       - :py:exc:`ImportError` -- package not installed in venv

       - :py:exc:`FileNotFoundError` -- yaml file not found within package

       - :py:exc:`strictyaml.exceptions.YAMLValidationError`
         -- yaml file validation failed

       - :py:exc:`AssertionError` -- Expecting one yaml file, many found

       - :py:exc:`logging_strict.LoggingStrictPackageNameRequired`
         -- Which package are the logging.config yaml in?

       - :py:exc:`logging_strict.LoggingStrictPackageStartFolderNameRequired`
         -- Within the provided package, the package base data folder name

    """
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
    except ImportError:
        raise
    except (FileNotFoundError, AssertionError):
        raise
    try:
        str_yaml = ui_yaml.as_str()
    except s.YAMLValidationError:
        raise

    # LoggingConfigYaml.setup is a wrapper of setup_logging_yaml
    # Checks: is_ok
    ui_yaml.setup(str_yaml, package_name=logger_package_name)


def ui_yaml_curated(
    genre,
    flavor,
    version_no=VERSION_FALLBACK,
    package_start_relative_folder="",
    logger_package_name=None,
):
    """Curated within |project_name| So do not have to provide package
    and package base data folder name

    :param genre:

       UI framework or worker implementation characteristic.
       E.g. textual, rich, :abbr:`mp (multiprocessing)`, or :abbr:`mq (rabbitmq)`

    :type genre: str
    :param flavor:

       Brand or how variation differs. e.g. :abbr:`asz (testing console UI)`

    :type flavor: str
    :param version_no: Default "1". Applies to genre or genre & flavor
    :type version_no: typing.Any | None
    :param package_start_relative_folder:

       Default empty string. Relative to package_data_folder_start.
       Relative path to further narrow down which folder contains the
       :py:mod:`logging.config` yaml file.

       Needed when multiple folders contain :py:mod:`logging.config` yaml file
       with same file name

    :type package_start_relative_folder: str
    :param logger_package_name:

       In logger dict, instead of the default package name, set a package name.
       Always desirable.

    :type logger_package_name: str | None
    """
    package_name = g_app_name
    package_data_folder_start = "configs"
    setup_ui_other(
        package_name,
        package_data_folder_start,
        genre,
        flavor,
        version_no=version_no,
        package_start_relative_folder=package_start_relative_folder,
        logger_package_name=logger_package_name,
    )


def worker_yaml_curated(
    genre="mp",
    flavor="asz",
    version_no=VERSION_FALLBACK,
    package_start_relative_folder="",
    logger_package_name=None,
):
    """For multiprocessing workers, retrieve the yaml in this order:

    - xdg user data dir folder

    - logging_strict package

    If QA tester, modifies the exported logging.config yaml, those
    changes are not overwritten

    Process 2nd step is calling:
    :py:func:`~logging_strict.logging_yaml_abc.setup_logging_yaml`

    :param genre:

       Default "mp". If UI: "textual" or "rich". If worker: "mp". Then can have
       a library of yaml files that can be used with a particular
       UI framework or worker type

    :type genre: str | None
    :param flavor:

       Default "asz". Unique identifier name given to a particular
       :py:mod:`logging.config` yaml. Should be one word w/o special characters

       Flavor is a very terse description, for a genre, how
       this yaml differs from others. If completely generic, call it
       ``generic``. If different handlers or formatters or filters are
       used, what is the yaml's purpose?

    :type flavor: str | None
    :param version_no:

       Default 1. Version of this particular
       :paramref:`~logging_strict.logging_api.worker_yaml_curated.params.genre`.
       **Not** the version of the yaml spec. Don't confuse the two.

    :type version_no: typing.Any | None
    :param package_start_relative_folder:

       Default empty string which means search the entire package.
       Further narrows down search, so as to differentiate between folders
       which contain file with the same file name

    :type package_start_relative_folder: pathlib.Path | str | None
    :param logger_package_name:

       Set logger to the intended package name. Default None which leaves as-is

    :type logger_package_name: str | None
    :returns: yaml file contents
    :rtype: str
    :raises:

       - :py:exc:`FileNotFoundError` -- yaml file not found within package

       - :py:exc:`strictyaml.exceptions.YAMLValidationError`
         -- yaml file validation failed

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

    # ImportError -- impossible. logging_strict package is installed
    try:
        ui_yaml.extract(path_relative_package_dir=package_start_relative_folder)
    except (FileNotFoundError, AssertionError):
        raise
    try:
        str_yaml = ui_yaml.as_str()
    except s.YAMLValidationError:
        raise

    # validation already occurred. In yaml, replace logger package name
    ret = after_as_str_update_package_name(
        str_yaml,
        logger_package_name=logger_package_name,
    )

    return ret


def setup_worker_other(
    package_name,
    package_data_folder_start,
    genre,
    flavor,
    version_no=VERSION_FALLBACK,
    package_start_relative_folder="",
    logger_package_name=None,
):
    """worker_yaml_curated grabs the logging.config yaml from logging-strict.
    Use this if located in another package

    Process 2nd step is calling:
    :py:func:`~logging_strict.logging_yaml_abc.setup_logging_yaml`

    :param package_name:

       If logging_strict, use method worker_yaml_curated instead. Otherwise
       package name which contains the logging.config yaml files

    :type package_name: str
    :param package_data_folder_start:

       Within
       :paramref:`~logging_strict.logging_api.setup_worker_other.params.package_name`,
       base data folder name. Not a relative path. Does not assume ``data``

    :type package_data_folder_start: str
    :param genre:

       Default "mp". If UI: "textual" or "rich". If worker: "mp". Then can have
       a library of yaml files that can be used with a particular
       UI framework or worker type

    :type genre: str
    :param flavor:

       Default "asz". Unique identifier name given to a particular
       :py:mod:`logging.config` yaml. Should be one word w/o special characters

       Flavor is a very terse description, for a
       :paramref:`~logging_strict.logging_api.setup_worker_other.params.genre`,
       how this yaml differs from others. If completely generic, call it
       ``generic``. If different handlers or formatters or filters are
       used, what is the yaml's purpose?

    :type flavor: str
    :param version_no:

       Default 1. Version of this particular
       :paramref:`~logging_strict.logging_api.setup_worker_other.params.genre`.
       **Not** the version of the yaml spec. Don't confuse the two.

    :type version_no: typing.Any | None
    :param package_start_relative_folder:

       Default empty string which means search the entire package.
       Further narrows down search, so as to differentiate between folders
       which contain file with the same file name

    :type package_start_relative_folder: pathlib.Path | str | None
    :param logger_package_name:

       Set logger to the intended package name. Default None which leaves as-is

    :type logger_package_name: str | None
    :returns: yaml file contents
    :rtype: str
    :raises:

       - :py:exc:`ImportError` -- package not installed in venv

       - :py:exc:`FileNotFoundError` -- yaml file not found within package

       - :py:exc:`strictyaml.exceptions.YAMLValidationError`
         -- yaml file validation failed

       - :py:exc:`AssertionError` -- Expecting one yaml file, many found

       - :py:exc:`logging_strict.LoggingStrictPackageNameRequired`
         -- Which package are the logging.config yaml in?

       - :py:exc:`logging_strict.LoggingStrictPackageStartFolderNameRequired`
         -- Within the provided package, the package base data folder name

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
    except ImportError:
        raise
    except (FileNotFoundError, AssertionError):
        raise
    try:
        str_yaml = ui_yaml.as_str()
    except s.YAMLValidationError:
        raise

    # validation already occurred. In yaml, replace logger package name
    str_yaml = after_as_str_update_package_name(
        str_yaml,
        logger_package_name=logger_package_name,
    )

    return str_yaml


class LoggingState:
    """Singleton to hold the current logging state.
    To know whether or not, run by app or from cli

    logging is redirected to

    - If run from app --> :py:exc:`textual.logging.TextualHandler`

    - If run from cli --> :py:class:`logging.StreamHandler`

    Knowing the logging mode (or state), first step towards restoring logging mode

    Class variables

    :cvar _instance: Default ``None``. Holds Singleton instance
    :type _instance: ``"LoggingState"`` | None
    :cvar _lock: Thread lock for Singleton
    :type _lock: threading.RLock

    .. seealso::

       See :py:mod:`textual.logging`

       Thread safe Singleton
       `[blog post] <https://medium.com/analytics-vidhya/how-to-create-a-thread-safe-singleton-class-in-python-822e1170a7f6>`_

    """

    _instance: "LoggingState" | None = None
    _lock = threading.RLock()
    # __state: bool | None = None

    def __new__(cls):
        """
        :returns: Singleton instance
        :rtype: ``"LoggingState"``
        """
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
    def reset(cls):
        """A cheat to reset the Singleton state. Use only during testing"""
        if cls._instance is not None:
            with cls._lock:
                if cls._instance:
                    cls._instance = None
                else:  # pragma: no cover
                    pass
        else:  # pragma: no cover
            pass

    @property
    def is_state_app(self):
        """Get logging state

        :returns: ``True`` if app logging state otherwise ``False``
        :rtype: bool | None
        """
        cls = type(self)
        with cls._lock:
            if hasattr(self, "_state"):
                ret = self._state
            else:
                ret = None

        return ret

    @is_state_app.setter
    def is_state_app(self, is_state_app):
        """Would only ever be changed within a unittest or module dealing with logging

        - ``True`` app logging state

        - ``False`` cli_logging state

        If not a bool, logging state is not changed

        :param is_state_app: New logging state. ``True`` if app otherwise ``False``
        :type is_state_app: typing.Any
        """
        cls = type(self)
        with cls._lock:
            is_param_ok = is_state_app is not None and isinstance(is_state_app, bool)
            if is_param_ok:
                self._state = is_state_app
            else:
                pass
