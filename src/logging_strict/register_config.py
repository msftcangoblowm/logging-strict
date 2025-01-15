r"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

Within the package root folder, ``logging_strict.yml`` is a catalog of
available logging config YAML files. Including test files

Record fields

.. code-block:: text

   - file:
       relative_path: configs/file_name_wo_suffixes
       category: worker
       genre: mp
       flavor: asz
       version_no: 1
       is_test_file: false

version_no value is cast to str

**Optional parameters**

is_test_file. Test files are marked to indicate shouldn't normally be
returned in a normal query. If true, will be returned

Workflow

1. In package base folder, check if a ``logging_strict.yml`` exists
2. validate the yaml file against a schema. Failure results in a INFO
   and a WARNING message
3. read in the yaml file contents
4. Allow a way to search/query
5. Have a way to mark bad files, resources intended only for testing

.. py:data:: REGEX_REL_PATH
   :type: str

   regex for posix relative path. Modified to:

   - include A-Z and underscore
   - the last negative lookbehind prevents trailing underscore period and hyphen

     ``path/file.html-``
     ``path/file.html.``
     ``path/file.html_``

.. seealso::

   `regex for relative path <https://stackoverflow.com/a/11383064>`_
   `tool to test regex <https://regex101.com/>`

Given a yaml str, what does strictyaml sees?

.. testcode::

    import strictyaml as s

    lst_expected = [{"file": {"a": "b", "c": "d"}}, {"file": {"b": "a", "d": "c"}}]
    obj_yaml = s.YAML(lst_expected)
    print(obj_yaml.as_yaml())

.. testoutput::
   :options: -ELLIPSIS, +NORMALIZE_WHITESPACE

   - file:
       a: b
       c: d
   - file:
       b: a
       d: c


Between ``- file:\\n`` and ``a: b\\n`` there are four spaces, not two.
Very helpful to understand difference between expected dict and needed yaml str
"""

from collections.abc import (
    Generator,
    Iterator,
    Mapping,
    MutableSet,
    Sequence,
)
from contextlib import nullcontext as does_not_raise
from functools import partial
from pathlib import (
    Path,
    PurePath,
)
from typing import TYPE_CHECKING
from unittest.mock import patch

import strictyaml as s

from .constants import (
    LoggingConfigCategory,
    g_app_name,
)
from .logging_api import (
    setup_ui_other,
    setup_worker_other,
)
from .logging_yaml_abc import VERSION_FALLBACK
from .logging_yaml_validate import validate_yaml_dirty
from .util.check_type import is_ok
from .util.package_resource import (
    PackageResource,
    _to_package_case,
    filter_by_file_stem,
    filter_by_suffix,
)
from .util.xdg_folder import DestFolderUser

# _logger = logging.getLogger(f"{g_app_name}.register_config")

CONFIG_STEM = "logging_strict"
CONFIG_SUFFIX = ".yml"
# REGEX_REL_PATH = "^(?!-)[_a-zA-Z0-9-]+(?<!-)(/(?!-)[_a-zA-Z0-9-]+(?<!-))*(/(?!-\.)[_a-zA-Z0-9-\.]+(?<![_\.-]))?$"
REGEX_REL_PATH = r"^(?!-)[_a-zA-Z0-9-]+(?<!-)(\/(?!-)[_a-zA-Z0-9-]+(?<!-))*(\/(?!-\.)[_a-zA-Z0-9-\.]+(?<![_\.-]))?$"

_category_values = s.Enum(["app", "worker"], item_validator=s.Str())

_item_map = s.MapCombined(
    {
        "relative_path": s.Regex(REGEX_REL_PATH),
        "category": _category_values,
        "genre": s.Str(),
        "flavor": s.Str(),
        "version_no": s.Str(),
        s.Optional("is_test_file", default=False, drop_if_none=True): s.Bool(),
    },
    s.Str(),
    s.Any(),
)

_file_map = s.Map({"file": _item_map})

_schema = s.Seq(_file_map)

test_yaml = """\
- file:
    relative_path: configs/worker.logging.config.yaml
    category: worker
    genre: mp
    flavor: asz
    version_no: 1
- file:
    relative_path: configs/textual_app.logging.config.yaml
    category: app
    genre: textual
    flavor: asz
    version_no: 1"""


class ExtractorLoggingConfig:
    """Extract both registry (YAML) db and a logging config YAML file

    :ivar package_name:

       Dirty package name of a package installed into venv.

    :vartype package_name: str
    :ivar path_alternative_dest_folder:

       The extraction folder, by default, is XDG User config folder.
       Support specifying an alternative folder.

       Having this feature baked in, would eleviate the need to use
       unittest.mock.patch and know what to patch

    :vartype path_alternative_dest_folder: pathlib.Path | None
    :ivar is_test_file: Default False. True if want to search for test files
    :vartype is_test_file: bool | None

    .. py:attribute:: __slots__
       :type: tuple[str, str, str, str, str, str, str]
       :value: ("_package_name", "_patch_extract_folder", "_path_extraction_dir", \
        "_is_test_file", "_path_extracted_db", "_logging_config_yaml_str", \
        "_registry", "_logging_config_yaml_relpath")

       Fixed class private attributes

    """

    __slots__ = (
        "_package_name",
        "_patch_extract_folder",
        "_path_extraction_dir",
        "_is_test_file",
        "_path_extracted_db",
        "_logging_config_yaml_str",
        "_registry",
        "_logging_config_yaml_relpath",
    )

    def __init__(
        self,
        package_name,
        path_alternative_dest_folder=None,
        is_test_file=False,
    ):
        """class constructor"""
        self.package_name = package_name

        # Specify alternative extraction folder
        if path_alternative_dest_folder is None:
            # When checking path, :code:`Path(None)` causes error
            is_set_to_xdg = True
        else:
            is_path = issubclass(type(path_alternative_dest_folder), PurePath)
            is_str = is_ok(path_alternative_dest_folder)
            if not is_path and not is_str:
                # unsupported type
                is_set_to_xdg = True
            else:
                if (
                    is_path
                    and path_alternative_dest_folder.is_absolute()
                    and path_alternative_dest_folder.is_dir()
                ):
                    self._patch_extract_folder = True
                    self._path_extraction_dir = path_alternative_dest_folder
                    is_set_to_xdg = False
                elif (
                    Path(path_alternative_dest_folder).is_absolute()
                    and Path(path_alternative_dest_folder).is_dir()
                ):
                    self._patch_extract_folder = True
                    self._path_extraction_dir = Path(path_alternative_dest_folder)
                    is_set_to_xdg = False
                else:
                    # relative path is bad or not a folder
                    is_set_to_xdg = True

        if is_set_to_xdg:
            self._patch_extract_folder = False
            self._path_extraction_dir = Path(DestFolderUser(self.package_name).data_dir)
        else:  # pragma: no cover
            pass

        if is_test_file is None or not isinstance(is_test_file, bool):
            self._is_test_file = False
        else:  # pragma: no cover
            self._is_test_file = is_test_file

        # Yet to be set
        self._path_extracted_db = None
        self._logging_config_yaml_str = None
        self._logging_config_yaml_relpath = None
        self._registry = None

    def __repr__(self):
        """Instance str representation

        :returns: str to reproduce instance
        :rtype: str
        """
        str_class_name = self.__class__.__name__
        ret = (
            f"<{str_class_name}("
            f"""'{self._package_name}', """
            f"""path_alternative_dest_folder='{self._path_extraction_dir.as_posix()}', """
            f"is_test_file={self._is_test_file})>"
        )
        return ret

    @staticmethod
    def clean_package_name(val):
        """Set raw package name. Is sanitized so it's a valid package name

        :param val: Should be a str. Raw package name
        :type val: typing.Any
        :returns: Clean package name
        :rtype: str | None
        """
        if is_ok(val):
            ret = _to_package_case(val)
        else:  # pragma: no cover
            ret = None

        return ret

    @property
    def package_name(self):
        """Get sanitized package name

        :returns: package name
        :rtype: str
        """
        return self._package_name

    @package_name.setter
    def package_name(self, val):
        """Set raw package name. Is sanitized so it's a valid package name

        :param val: Should be a str. Raw package name
        :type val: typing.Any
        """
        cls = type(self)
        package_name_clean = cls.clean_package_name(val)
        if package_name_clean is not None:
            self._package_name = package_name_clean
        else:  # pragma: no cover
            pass

    @property
    def path_extracted_db(self):
        """After
        :py:meth:`logging_strict.register_config.ExtractorLoggingConfig.extract_db`
        will hold the path to the registry db YAML file

        :returns: logging config YAML registry db path. registry db is also a YAML file
        :rtype: pathlib.Path | None
        """
        return self._path_extracted_db

    @property
    def is_test_file(self):
        """True if should extract a test files otherwise extract normal
        logging strict YAML files

        :returns:

           True extract a test file. False extract normal file

        :rtype: bool
        """
        return self._is_test_file

    @property
    def logging_config_yaml_str(self):
        """Get query_db result

        UI -- will return a logging config dict

        WORKER -- logging config returns a yaml str.
        Multiprocessing situation can only pass str, not a dict

        :returns: validated logging config YAML str otherwise None
        :rtype: str | dict[str, typing.Any] | None
        """
        return self._logging_config_yaml_str

    @property
    def logging_config_yaml_relpath(self):
        """Get query_db result absolute path to destination  logging config YAML file

        :returns: absolute path
        :rtype: str | None
        """
        return self._logging_config_yaml_relpath

    def extract_db(self):
        """Extract logging config YAML file registry db. Implementation
        is YAML so can be validated.

        If no such package installed, Logs a warning. Does not raise ImportError
        """
        if TYPE_CHECKING:
            from .util.package_resource import (
                PartStem,
                PartSuffix,
            )

            cb_stem: PartStem
            cb_suffix: PartSuffix

        start_folder_relpath = ""
        pr = PackageResource(self._package_name, start_folder_relpath)
        cb_stem = partial(filter_by_file_stem, CONFIG_STEM)
        cb_suffix = partial(filter_by_suffix, CONFIG_SUFFIX)
        # msg_info = f"cb_suffix {cb_suffix!r}"
        # _logger.info(msg_info)

        # Generator not called yet, no ImportError
        gen_files = pr.package_data_folders(
            cb_suffix=cb_suffix,
            cb_file_stem=cb_stem,
        )

        # Exceptions logged WARNING level
        iter_path_f = pr.resource_extract(
            gen_files,
            self._path_extraction_dir,
            cb_suffix=cb_suffix,
            cb_file_stem=cb_stem,
            is_overwrite=True,
        )
        lst_files = list(iter_path_f)
        lst_files_count = len(lst_files)
        # print(f"extract_db file count ({lst_files_count}) {lst_files}", file=sys.stderr)
        if lst_files_count >= 1:
            # Take the 1st result although there should only be one file
            self._path_extracted_db = lst_files[0]
        else:  # pragma: no cover
            # Failed query. In package, no such data file
            self._path_extracted_db = None

    def get_db(self, path_extracted_db=None):
        """Get YAML registry of logging config YAML file records. Which happens
        also to be a YAML file.

        If package not installed, will emit INFO and WARNING log messages

        :param path_extracted_db:

           Default None. None extract registry otherwise restore previously
           extracted YAML registry from file

        :type path_extracted_db: pathlib.Path | None
        :returns: On success entire database. None if database file not found
        :rtype: collections.abc.Sequence[dict[str, dict[str, str]]] | None
        :raises:

           - :py:exc:`strictyaml.YAMLValidationError` -- validation failed

        """
        # On failure, :code:`self._path_extracted_db is None` and a warning is logged
        if path_extracted_db is not None:
            if (
                issubclass(type(path_extracted_db), PurePath)
                and path_extracted_db.exists()
                and path_extracted_db.is_file()
            ):
                self._path_extracted_db = path_extracted_db
                is_extract = False
            else:
                # unsupported type
                is_extract = True
        else:
            is_extract = True

        if is_extract is True:
            self.extract_db()
        else:  # pragma: no cover
            pass

        path_f = self.path_extracted_db
        if path_f is None:
            # Failed query. In package, no such data file
            self._registry = None
        else:
            str_yaml_raw = path_f.read_text()
            # validate database against schema
            try:
                yaml_config = validate_yaml_dirty(
                    str_yaml_raw,
                    schema=_schema,
                )
            except s.YAMLValidationError:
                raise
            else:
                # when patched, this method didn't end at the :code:`raise`
                self._registry = yaml_config.data

    def query_db(
        self,
        category,
        genre=None,
        flavor=None,
        version_no=VERSION_FALLBACK,
        logger_package_name=None,
        is_skip_setup=True,
    ):
        """Query the database

        Result available from property logging_config_yaml_str

        Does not emit log messages

        :param category: worker or app. Unfortunitely the default is app.
        :type category: logging_strict.constants.LoggingConfigCategory | str | typing.Any | None
        :param genre:

           Library or how the logging config YAML file is applied. If
           UI: "textual". If worker: "mp". More will be added over time

        :type genre: str | None
        :param flavor: The brand or package which first used this logging config YAML file
        :type flavor: str | None
        :param version_no:

           Default "1". The logging config YAML file version no. Previous versions
           are not necessarily removed unless it's known no one on the planet is using it.

        :type version_no: str | None
        :param logger_package_name:

           Default None. In the logging config YAML file, replaces default
           logger token with package name that will be logged

        :type logger_package_name: str | None
        :param is_skip_setup:

           Default True. During querying, avoid (UI only) setup.
           Logging setup can raise errors, such as ModuleNotFoundError

        :type is_skip_setup: bool | None
        """
        if is_ok(logger_package_name):
            str_logger_package_name = logger_package_name
        else:
            str_logger_package_name = None

        is_set_blank = True
        if self._registry is None or not isinstance(
            self._registry,
            (Generator, Sequence, Iterator, set, MutableSet),
        ):
            # No Registry. Cannot extract and validate
            is_set_blank = True
        else:
            for d_record in self._registry:
                assert isinstance(d_record, Mapping)
                d_item = d_record["file"]
                # should be a posix path to a logging config YAML file
                item_f_relpath = d_item["relative_path"]
                item_category = d_item["category"]
                item_genre = d_item["genre"]
                item_flavor = d_item["flavor"]
                item_version_no = d_item["version_no"]
                # Optional field. If not provided, schema automagically sets default
                item_is_test_file = d_item["is_test_file"]

                # Either both test file or both normal file
                # not a test file and want a test file
                is_mismatch_not_a_test = (
                    self.is_test_file is False and item_is_test_file is True
                )
                # is a test file, but don't want a test file
                is_mismatch_not_a_normal = (
                    self.is_test_file is True and item_is_test_file is False
                )
                is_mismatch = is_mismatch_not_a_test or is_mismatch_not_a_normal
                is_category_mismatch = is_ok(category) and category != item_category
                is_genre_mismatch = is_ok(genre) and genre != item_genre
                is_flavor_mismatch = is_ok(flavor) and flavor != item_flavor
                is_version_no_mismatch = (
                    is_ok(version_no) and version_no != item_version_no
                )

                t_skip = (
                    is_mismatch,
                    is_category_mismatch,
                    is_genre_mismatch,
                    is_flavor_mismatch,
                    is_version_no_mismatch,
                )
                is_skip = any(t_skip)

                if is_skip:
                    continue
                else:
                    pass

                """Choose which extraction function to use based only on category

                Do not call worker_yaml_curated or ui_yaml_curated.
                ``package_data_folder_start`` is hardcoded.
                """
                if category == LoggingConfigCategory.UI.value:
                    fcn = setup_ui_other
                else:
                    # Default to LoggingConfigCategory.WORKER.value
                    fcn = setup_worker_other

                # Is package data so will need to extract package data file
                # Separate relpath into components. Get relative path without file name
                relpath_f = Path(item_f_relpath)
                if str(relpath_f.parent) == ".":
                    package_start_relative_folder = ""
                else:
                    package_start_relative_folder = str(relpath_f.parent)

                # Extract the logging config YAML file
                fcn_wo_params = partial(
                    fcn,
                    self.package_name,
                    package_start_relative_folder,
                    item_genre,
                    item_flavor,
                    version_no=item_version_no,
                    package_start_relative_folder=package_start_relative_folder,
                    logger_package_name=str_logger_package_name,
                )
                if is_skip_setup:
                    # logging config defang. Skip setup to avoid possible exceptions
                    cm_skip = patch(
                        "logging.config.dictConfig",
                        return_value=True,
                    )
                else:
                    # Do not skip setup
                    cm_skip = does_not_raise()

                try:
                    is_xdg_folder = self._patch_extract_folder is False
                    if is_xdg_folder:
                        with cm_skip:
                            t_ret = fcn_wo_params()
                    else:
                        # alternative extraction folder
                        with (
                            cm_skip,
                            patch(
                                f"{g_app_name}.util.xdg_folder._get_path_config",
                                return_value=self._path_extraction_dir,
                            ),
                            patch(
                                f"{g_app_name}.logging_yaml_abc._get_path_config",
                                return_value=self._path_extraction_dir,
                            ),
                            patch(
                                f"{g_app_name}.logging_api._get_path_config",
                                return_value=self._path_extraction_dir,
                            ),
                        ):
                            t_ret = fcn_wo_params()
                except (FileNotFoundError, AssertionError):
                    """Inappropriate location to validate ``logging_strict.yml``

                    FileNotFoundError -- register db contains entry but
                    the package data file is missing.

                    AssertionError -- More than one logging config YAML file found.
                    """
                    continue
                except s.YAMLValidationError:
                    """Inappropriate location to validate ``logging_strict.yml``

                    strictyaml.YAMLValidationError -- logging config
                    YAML file validation failed.
                    """
                    continue
                else:
                    is_set_blank = False
                    f_relpath, str_yaml = t_ret
                    self._logging_config_yaml_relpath = f_relpath
                    self._logging_config_yaml_str = str_yaml
                    # match was found. Stop the for loop
                    break
            else:
                # config file has no records
                is_set_blank = True

        if is_set_blank:
            self._logging_config_yaml_relpath = None
            self._logging_config_yaml_str = None
        else:  # pragma: no cover
            pass
