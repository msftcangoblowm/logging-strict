"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

..

Extracts package resource data

- works!
- intuitive
- flexible
- static type checks

The Problem
------------

Some Python package authors create bash scripts to find a folder,
using :code:`Path(__file__).parent` which contains their data
files.

Understandably, the UX of working with Python package data is beyond
their patience level.

This module is for those who want the UX of extracting package data
to be easy. Enough that they'll go back and remove all those ugly
hacks and bash scripts.

.. note:: :py:meth:`PackageResource.package_data_folders <logging_strict.util.package_resource.PackageResource.package_data_folders>` yields data folders

   First step to extracting package data is to narrow down the
   (package) folders. The Second step is extracting the data files.

Example
---------

Extract package data to local cache

package data folder: ``data/currency``

Note the path is relative

Local cache folder: :code:`$HOME/.cache/[package name]`

.. code-block:: python

    import sys
    from typing import TYPE_CHECKING
    from collections.abc import Iterator
    from functools import partial
    from pathlib import PurePath
    from logging_strict.util.package_resource import filter_by_suffix
    from logging_strict.util.package_resource import filter_by_file_stem
    from logging_strict.util.package_resource import PartSuffix
    from logging_strict.util.package_resource import PartStem
    from logging_strict.util.package_resource import package_data_folders
    from logging_strict.util.package_resource import cache_extract

    if sys.version_info >= (3, 9):  # pragma: no cover
        try:
            from importlib.resources.abc import Traversable  # py312+
        except ImportError:
            from importlib.abc import Traversable  # py39+
    else:  # pragma: no cover
        msg_exc = "Traversable py39+"
        raise ImportError(msg_exc)

    if TYPE_CHECKING:
        data_folder_path: str
        cb_file_stem: PartStem
        cb_file_suffix: PartSuffix
        generator_folders: Iterator[Traversable]
        path_entry: type[PurePath]

    data_folder_path = "data/currency"
    cb_file_stem = partial(filter_by_file_stem, "crypto_btc_default")
    cb_file_suffix = partial(filter_by_suffix, ".bitcoin")
    generator_folders = package_data_folders(
        cb_suffix=cb_file_suffix,
        cb_file_stem=cb_file_stem,
        package_name="decimals",
        path_relative_package_dir=data_folder_path,
    )
    for path_entry in cache_extract(
        generator_folders,
        package_name,
        cb_suffix=cb_file_suffix,
        cb_file_stem=cb_file_stem,
        is_overwrite=False,
    ):
        # path_entry is the extracted file path in local cache
        pass


So our file, :code:`data/currency/crypto_btc_default.bitcoin` is
extracted into folder :code:`$HOME/.cache/[package name]/data/currency`

For more fine control, options are:

- move it within the cache_extract for loop

- :py:meth:`PackageResource.resource_extract <logging_strict.util.package_resource.PackageResource.resource_extract>`

.. note:: DIY

   Especially
   :py:func:`~logging_strict.util.package_resource.filter_by_file_stem`,
   but this might apply to
   :py:func:`~logging_strict.util.package_resource.filter_by_suffix`
   as well, these are for the simplest scenerio. They are both just a
   normal function. If/when necessary, roll your own

.. note:: package_data_folders param :py:obj:`package_data_folders.package_name <logging_strict.util.package_resource.PackageResource.package_data_folders.params.package_name>`

   Change to whichever package contains the data files you are interested
   in. Not the package in this example


Module private variables
-------------------------

.. py:data:: __all__
   :type: tuple[str, str, str, str, str]
   :value: ("filter_by_suffix", "filter_by_file_stem", \
   "PackageResource", "PartSuffix", "PartStem")

   Module object exports

.. py:data:: is_module_debug
   :type: bool
   :value: False

   During development, turns on logging. Once unittest cover reaches
   100%, turn off

.. py:data:: g_module
   :type: str
   :value: logging_strict.util.package_resource

   logging dotted path

.. py:data:: _LOGGER
   :type: logging.Logger

   Complicated module. Does issue logging warnings


Module objects
---------------

"""

from __future__ import annotations

import importlib.resources as importlib_resources  # py39+
import logging
import re
import shutil
import sys
import traceback
from contextlib import suppress  # py39+
from importlib.metadata import (
    PackageNotFoundError,
    distribution,
)
from pathlib import (
    Path,
    PurePath,
)
from typing import (
    TYPE_CHECKING,
    Any,
    cast,
)

from ..constants import g_app_name
from .check_type import is_ok
from .util_root import IsRoot
from .xdg_folder import DestFolderUser

if sys.version_info >= (3, 8):  # pragma: no cover
    from collections.abc import (  # noqa: F401 sphinx uses
        Callable,
        Iterator,
        Sequence,
    )
    from typing import (
        Protocol,
        runtime_checkable,
    )
else:  # pragma: no cover
    from typing import (  # noqa: F401 sphinx uses
        Callable,
        Iterator,
        Sequence,
    )

    from typing_extensions import (
        Protocol,
        runtime_checkable,
    )

if sys.version_info >= (3, 9):  # pragma: no cover
    try:
        from importlib.resources.abc import Traversable  # py312+
    except ImportError:  # pragma: no cover
        from importlib.abc import Traversable  # py39+
else:  # pragma: no cover
    msg_exc = "Traversable py39+"
    raise ImportError(msg_exc)

__all__ = (
    "filter_by_suffix",
    "filter_by_file_stem",
    "PackageResource",
    "PartSuffix",
    "PartStem",
)

is_module_debug = False
g_module = f"{g_app_name}.util.package_resource"
_LOGGER = logging.getLogger(g_module)


def msg_stem(file_name):
    """:py:attr:`pathlib.Path.stem` is not ideal, actually it's
    misleading, expecting file name without any suffixes.

    Instead what happens, if there are many suffixes, only
    one suffix is removed. Would like to remove **all**
    suffixes, not just one

    This is counter-intuitive

    .. code-block:: python

        assert Path.stem("asdf.onnx.json") == "asdf.onnx"

    What :py:func:`msg_stem` does

    .. code-block:: python

        assert msg_stem("asdf.onnx.json") == "asdf"


    :param file_name: A file name or file path
    :type file_name: str | pathlib.Path
    :returns: file name without any file extensions
    :rtype: str

    .. warning:: file_name not Optional

       Use with either :py:class:`~pathlib.Path` or :py:class:`str`,
       not ``None``


    """
    if TYPE_CHECKING:
        msg_warn: str
        ret: str | None
        path_name: Path
        name_path: str
        lst_suffixes: list[str]
        suffix_all: str

    msg_warn = "No file name empty string or None. Both are not allowed"

    if file_name is not None and issubclass(type(file_name), PurePath):
        path_name = file_name
        name_path = file_name.name
    elif is_ok(file_name):
        path_name = Path(file_name)
        name_path = Path(file_name).name
    else:
        path_name = None
        name_path = None

    if name_path is not None:
        lst_suffixes = path_name.suffixes
        if len(lst_suffixes) == 0:
            ret = name_path
        else:
            suffix_all = "".join(lst_suffixes)
            ret = name_path[: -len(suffix_all)]
    else:
        ret = None

    if ret is None:
        raise ValueError(msg_warn)
    else:  # pragma: no cover
        pass

    return cast(str, ret)


# https://stackoverflow.com/a/66664521
@runtime_checkable
class PartSuffix(Protocol):
    """Type of suffix callback functions

    Usage

    .. code-block:: python

        from typing import TYPE_CHECKING
        from functools import partial
        from logging_strict.package_resource import filter_by_suffix
        from logging_strict.package_resource import PartSuffix

        if TYPE_CHECKING:
            cb_suffix: PartSuffix
        cb_suffix = partial(filter_by_suffix, (".svg", ".png"))
        cb_suffix = partial(filter_by_suffix, ".toml")

    :param expected_suffix: Suffix or suffixes to search for
    :type expected_suffix: str | tuple[str, ...]
    :param test_suffix: file name or file suffixes concatenated
    :type test_suffix: str
    :returns: ``True`` if suffix(es) match otherwise ``False``
    :rtype: bool
    """

    def __call__(
        fakeSelf,
        expected_suffix,
        test_suffix,
    ):  # pragma: no cover
        """Empty Implementation. Protocol usage is as a type"""
        pass


@runtime_checkable
class PartStem(Protocol):
    """file stem callback functions
    Careful! Will return all files that match the file stem

    Usage

    .. code-block:: python

        from typing import TYPE_CHECKING
        from functools import partial
        from logging_strict.util.package_resource import filter_by_file_stem
        from logging_strict.util.package_resource import PartStem

        if TYPE_CHECKING:
            cb_file_stem: PartStem

        cb_file_stem = partial(filter_by_file_stem, file_name)
        cb_file_stem = partial(filter_by_file_stem, "index.theme")

    :param file_expected:

       File stem to search for. Can provide file name

    :type file_expected: str
    :param test_file_stem: file name or stem to test for
    :type test_file_stem: str
    :returns: ``True`` if file stem matches otherwise ``False``
    :rtype: bool
    """

    def __call__(
        fakeSelf,
        file_expected,
        test_file_stem,
    ):  # pragma: no cover
        """Empty Implementation. Protocol usage is as a type"""
        pass


def match_file(y, /, *, cb_suffix=None, cb_file_stem=None):
    """The callbacks act as filters to check whether this file is
    a match according to our requirements

    Terminology is :menuselection:`x, y --> folder, file`

    :param y: A traversable file
    :type y: importlib.resources.abc.Traversable
    :param cb_suffix:

       Function creating using :py:func:`functools.partial` which
       filters by suffix

    :type cb_suffix: collections.abc.Callable[[str],bool] | None
    :param cb_file_stem:

       Function creating using :py:func:`functools.partial` which
       filters by file name stem

    :type cb_file_stem: collections.abc.Callable[[str],bool] | None
    :returns: True if a match otherwise False
    :rtype: bool
    """
    if TYPE_CHECKING:
        ret: bool
        suffixes: list[str]
        suffix: str
        is_filter_suffix: bool
        str_name: str
        stem: str
        is_filter_file_stem: bool

    ret = False
    if isinstance(y, Traversable) and y.is_file():
        # file_name_pkg = traversable_file.name
        # Check suffix
        suffixes = Path(y.name).suffixes
        suffix = "".join(suffixes)
        is_filter_suffix = cb_suffix is None or cb_suffix(suffix)

        # Check file name stem
        str_name = y.name
        stem = msg_stem(str_name)
        is_filter_file_stem = cb_file_stem is None or cb_file_stem(stem)

        ret = is_filter_suffix and is_filter_file_stem

    return ret


def check_folder(x, cb_suffix=None, cb_file_stem=None):
    """Check folder
    Terminology is :menuselection:`x, y --> folder, file`

    :param x: A traversable folder
    :type x: importlib.resources.abc.Traversable
    :param cb_suffix:

       Function creating using :py:func:`functools.partial` which
       filters by suffix

    :type cb_suffix: collections.abc.Callable[[str],bool] | None
    :param cb_file_stem:

       Function creating using :py:func:`functools.partial` which
       filters by file name stem

    :type cb_file_stem: collections.abc.Callable[[str],bool] | None
    :returns:

       if a match, yield :paramref:`x`

    :rtype: collections.abc.Iterator[importlib.resources.abc.Traversable]
    """
    if TYPE_CHECKING:
        is_found_target_file: bool
        is_match: bool
        y: Traversable

    if not isinstance(x, Traversable):  # pragma: no cover
        yield from ()
    else:
        is_found_target_file = False

        for y in x.iterdir():
            is_match = match_file(
                y,
                cb_suffix=cb_suffix,
                cb_file_stem=cb_file_stem,
            )
            if is_match:
                is_found_target_file = True
            else:  # pragma: no cover
                pass

        # yield the folder, not the files
        if is_found_target_file:
            yield x
        else:
            yield from ()


def filter_by_suffix(expected_suffix, test_suffix):
    """Usage

    .. code-block:: python

        from functools import partial
        from logging_strict.package_resource import filter_by_suffix, PartSuffix

        cb_suffix: PartSuffix = partial(filter_by_suffix, expected_suffix)
        ...

    Then use ``cb_suffix`` as kwarg to
    :py:meth:`PackageResource.cache_extract <logging_strict.util.package_resource.PackageResource.cache_extract>`

    :param expected_suffix: Suffix (e.g. ".ppn") searching for
    :type expected_suffix: str | tuple[str, ...]
    :param test_suffix: The file name suffix testing against
    :type test_suffix: str
    :returns: ``True`` if same otherwise ``False``
    :rtype: bool
    """
    if TYPE_CHECKING:
        ret: bool
        is_found: bool
        suffix: str

    def is_empty(val: Any) -> bool:
        """None or empty str

        :param val: Value to check
        :type val: typing.Any
        :returns: True if passes check
        :rtype: bool
        """
        return val is None or isinstance(val, str) and len(val) == 0

    def is_not_empty(val: Any) -> bool:
        """Not None and non-empty str

        :param val: Value to check
        :type val: typing.Any
        :returns: True if passes check
        :rtype: bool
        """
        return val is not None and isinstance(val, str) and len(val) != 0

    if is_empty(expected_suffix) and is_empty(test_suffix):
        # Both None or empty string
        ret = True
    elif (
        is_not_empty(expected_suffix)
        and is_not_empty(test_suffix)
        and test_suffix.endswith(expected_suffix)
    ):
        ret = True
    elif isinstance(expected_suffix, tuple):
        is_found = False
        for suffix in expected_suffix:
            if (
                is_not_empty(suffix)
                and is_not_empty(test_suffix)
                and test_suffix.endswith(suffix)
            ):
                is_found = True
                break
        ret = is_found
    else:
        ret = False

    return ret


def filter_by_file_stem(expected_file_name, test_file_name):
    """This is the simpliest case, simple matching of package
    resource file name against expected file name

    Usage

    .. code-block:: python

        from functools import partial
        from logging_strict.util.package_resource import filter_by_file_stem

        cb_file_stem = partial(filter_by_file_stem, expected_file_name)
        ...

    ``cb_file_stem`` is used extensively within this module

    :param expected_file_name:

       file name or stem. Are search for this

    :type expected_file_name: str
    :param test_file_name: The file name suffix testing against
    :type test_file_name: str
    :returns: ``True`` if same otherwise ``False``
    :rtype: bool

    .. note:: This is the simpliest case

       For more complex cases write a lambda or function and
        use :py:func:`functools.partial` to create a callback


    """
    if TYPE_CHECKING:
        ret: bool

    ret = expected_file_name is None or msg_stem(expected_file_name) == msg_stem(
        test_file_name
    )

    return ret


def _extract_folder(package):
    """Mockable to change the destination folder

    Use only by
    :py:meth:`logging_strict.util.package_resource.PackageResource.cache_extract`
    so can override destination folder

    :param package: package name
    :type package: str
    :returns: cache folder
    :rtype: str
    """
    ret = DestFolderUser(package).cache_dir
    return ret


def walk_tree_folders(traversable_root):
    """:py:meth:`importlib.resources.files` returns a single
    :py:class:`~importlib.resources.abc.Traversable` which is
    the Python3 package root folder. A
    :py:class:`~importlib.resources.abc.Traversable` supports
    :py:meth:`pathlib.Path.iterdir`, but not :py:meth:`pathlib.Path.glob`.

    :param process_name: package data folder or a subfolder
    :type process_name: importlib.resources.abc.Traversable
    :returns: The entire sub-tree. Includes self
    :rtype:

       collections.abc.Iterator[importlib.resources.abc.Traversable]

    """
    if TYPE_CHECKING:
        traversable_x: Traversable

    ignores = ("__pycache__",)

    for traversable_x in traversable_root.iterdir():
        if traversable_x.is_dir():
            if traversable_x.name not in ignores:
                yield traversable_x
                yield from walk_tree_folders(traversable_x)
            else:  # pragma: no cover blacklisted folder
                pass

    yield from ()


def is_package_exists(package_name):
    """Discover whether a python package is installed within
    virtual environment

    :param package_name: python package name
    :type package_name: str
    :returns: Whether or not python package found
    :rtype: bool
    """
    if TYPE_CHECKING:
        ret: bool

    # Available in python3.10
    # :py:meth:`importlib.metadata.packages_distributions`
    try:
        distribution(package_name)
    except PackageNotFoundError:
        ret = False
    else:
        ret = True

    return ret


def _to_package_case(val):
    """Sanitize package name to a valid dotted path

    The ultimate test is
    :py:func:`logging_strict.util.package_resource._get_package_data_folder`.
    Which wraps :py:func:`importlib_resources.files`. Expects a dotted path.

    If :py:func:`importlib_resources.files` doesn't get a valid dotted path,
    returns None. Which can be unexpected.

    Acts as a mitigation fix to allow for understandable simple human
    errors.

    :param val:

       An arbitrary str. Unallowed chars will be converted into hyphens

    :type val: str
    :returns:

       Valid package name can contain: alphanumeric, underscore, or period chars.
       A period denotes a namespace package

    :rtype: str
    """
    ret = re.sub("[^a-z0-9.]+", "_", val.lower())

    return ret


def _get_package_data_folder(dotted_path):
    """Helper that retrieves the package resource

    If :py:func:`importlib_resources.files` doesn't get a valid dotted path,
    returns None. Which can be unexpected.

    Better UX would allow for understandable simple human errors.

    Mitigate by fixing weird characters --> underscore. While allowing
    namespace packages (e.g. ``zope.interface``).

    With the mitigation fix, None means the package is not installed
    rather than a hard to track down typo.

    :param dotted_path: package_name and optionally dotted path to a subfolder
    :type dotted_path: str
    :returns:

       The traversable path. Either a package root or a subfolder

    :rtype: importlib.resources.abc.Traversable | None
    """
    dotted_path_valid = _to_package_case(dotted_path)
    try:
        trav_ret = importlib_resources.files(dotted_path_valid)
    except ModuleNotFoundError:
        # There is no such package or data folder
        trav_ret = None

    return trav_ret


class PackageResource:
    """In a Python package, could be any package installed into
    the virtual environment, which package data folder is the
    base folder in which to start the search for data files.
    As in a fallback folder

    Do not assume the default start data folder is ``data``. Impose rule
    that data files must not be stored in the package base folder; must be
    placed into a folder

    :ivar package: package name
    :vartype package: str
    :ivar package_data_folder_start: package base data folder name. Not relative path
    :vartype package_data_folder_start: str
    """

    def __init__(self, package, package_data_folder_start):
        """Class constructor"""
        super().__init__()
        self._package = package
        self._package_data_folder_start = package_data_folder_start

    @property
    def package(self):
        """Package name

        :returns: package name
        :rtype: str
        """
        return self._package

    @property
    def package_data_folder_start(self):
        """Package name

        :returns: package base data folder name. Not relative path
        :rtype: str
        """
        return self._package_data_folder_start

    def path_relative(
        self,
        y,
        /,
        *,
        path_relative_package_dir=None,
        parent_count=None,
    ):
        """Whilst traversing package data, a data file's path, relative
        to a package folder, usually root folder, is unavailable.
        Only have the absolute path of the extracted data file

        This limits flexibility. There might be need, especially
        during testing, to move the extracted data file to another
        folder


        An Example
        :paramref:`~logging_strict.util.package_resource.PackageResource.path_relative.params.y`
        which is an absolute path package data extracted by
        :py:func:`importlib.resources.as_file`. Which should be zip safe

        .. code-block:: text

           [venv path]/lib/python3.9/site-packages/decimals/data/currency/digital_tox_default.ini


        Code sample is not extracting package data, instead fakes an
        absolute path, which needs to contain folder "data" although
        the local cache wouldn't have this folder.

        >>> from pathlib import Path
        >>> from logging_strict.constants import g_app_name
        >>> from logging_strict.util.package_resource import (
        ...     PackageResource,
        ...     _extract_folder,
        ... )
        >>> path_local_cache = Path(_extract_folder(g_app_name))
        >>> y = path_local_cache.joinpath(
        ...     "data", "currency", "nonsense", "digital_tox_default.ini"
        ... )
        >>> pr = PackageResource("some package name", "data")
        >>> pr.path_relative(y, parent_count=None)
        PosixPath('currency/nonsense/digital_tox_default.ini')
        >>> pr.path_relative(y, parent_count=0)
        PosixPath('digital_tox_default.ini')
        >>> pr.path_relative(y, parent_count=1)
        PosixPath('nonsense/digital_tox_default.ini')
        >>> pr.path_relative(y, parent_count=2)
        PosixPath('currency/nonsense/digital_tox_default.ini')
        >>> pr.path_relative(y, parent_count=3)  # can't do beyond start dir, "data"
        PosixPath('currency/nonsense/digital_tox_default.ini')


        :param y: Extracted data file's path
        :type y: pathlib.Path
        :param path_relative_package_dir:

           Default "data" (folder). Relative package path. Treat a
           base folder

        :type path_relative_package_dir: :py:class:`~pathlib.Path` | str | None
        :param parent_count:

           Ignoring file name.
           Default ``None`` indicates entire relative path. Return
           x folders, from parent, working backwards

        :type parent_count: int | None
        :returns:

           Relative path excluding from
           :paramref:`~logging_strict.util.package_resource.PackageResource.path_relative.params.path_relative_package_dir`

        :rtype: pathlib.Path

        :raises:

           - :py:exc:`TypeError` -- ``None``, not a type[PurePath] or
             relative path

           - :py:exc:`LookupError` -- Cannot return relative path from
             non-existing parent folder

        """
        if TYPE_CHECKING:
            operation: str
            msg_exc: str
            path_relative_to: Path
            file_name: str
            last_folder_name: str
            lst_parts: list[str]
            idx: int
            path_relative_reversed: Path
            parents: list[str]
            ret: Path

        operation = "path_relative"

        if (
            y is None
            or not issubclass(type(y), PurePath)
            or (issubclass(type(y), PurePath) and not y.is_absolute())
        ):
            msg_exc = f"In {operation}, expects an absolute Path"
            raise TypeError(msg_exc)

        if path_relative_package_dir is None:
            path_relative_package_dir = Path(self.package_data_folder_start)
        else:  # pragma: no cover
            pass

        if path_relative_package_dir is not None and isinstance(
            path_relative_package_dir, str
        ):
            # Any str will work
            path_relative_to = Path(path_relative_package_dir)
        elif path_relative_package_dir is not None and issubclass(
            type(path_relative_package_dir), PurePath
        ):
            path_relative_to = path_relative_package_dir
        else:
            path_relative_to = Path(self.package_data_folder_start)

        file_name = y.name
        last_folder_name = path_relative_to.name

        #####
        # Case: file in root folder
        #####
        if last_folder_name == str(y.parent.name):
            return Path(file_name)

        ######
        # Case: For resources in sub-folders
        ######
        lst_parts = list(y.parts)

        # careful: in-place
        lst_parts.reverse()

        try:
            # Lookup. Is last_folder_name in lst_parts?
            idx = lst_parts.index(last_folder_name)
        except ValueError as e:
            # path_relative_reversed = Path(*lst_parts[:1])
            msg_exc = (
                f"In {operation}, folder {last_folder_name} not in "
                f"{str(y.parent)}. Can not return relative path from "
                "non-existing parent"
            )
            raise LookupError(msg_exc) from e
        else:
            path_relative_reversed = Path(*lst_parts[:idx])

        lst_playing = list(path_relative_reversed.parts)
        lst_playing.remove(file_name)

        parents = []

        if parent_count is None:
            # Take all relative folders
            parents.extend(lst_playing)
        else:
            for num in range(0, parent_count):
                if len(lst_playing) != 0:
                    parents.append(lst_playing.pop(0))

        parents.reverse()
        ret = Path(*parents).joinpath(file_name)

        return ret

    def get_parent_paths(
        self,
        *,
        cb_suffix=None,
        cb_file_stem=None,
        path_relative_package_dir=None,
        parent_count=1,
    ):
        """Example from a package there is a resource:

        ``data/theme/size/category/[image file name]``

        The relative path is extracted. In this case, ``data``,
        which is relevent only to the package, not to the final file
        system location. Interested in a relative path, not the absolute
        path from POV of the package

        Remaining path

        theme/size/category/[image file name]

        resource: [image file name]

        Parents: ["theme", "size", "category"]

        The cb_suffix and cb_file_stem selects the relevent file

        .. caution:: Location of package data files

           **CANNOT** be in the base folder of a package. Move any
           package data files into an appropriately named/categoried
           sub-folder.

           Strong assumption that there will never be data files in the
           package base folder. And if so, those aren't data files, that's
           clutter

        :param cb_suffix:

           Function creating using :py:func:`functools.partial`
           which filters by suffix

        :type cb_suffix: collections.abc.Callable[[str],bool] | None
        :param cb_file_stem:

           Function creating using :py:func:`functools.partial` which
           filters by file name stem

        :type cb_file_stem: collections.abc.Callable[[str],bool] | None
        :param path_relative_package_dir:

           package base folder to start the search. ``None`` becomes the
           :py:obj:`PackageResource.package_data_folder_start <logging_strict.util.package_resource.PackageResource.package_data_folder_start>`,
           not the package base folder. Assumes package authors are smart
           and would never be that gullible.

        :type path_relative_package_dir: pathlib.Path | str | None
        :param parent_count:

           Default 1. Retrieve x number of parent folder names

        :type parent_count: int | None
        :returns: file name and respective parents as an Sequence[str]
        :rtype: dict[str, Sequence[str]] | None
        """
        if TYPE_CHECKING:
            path_relative_to: Path
            d_files: dict[str, tuple[str, ...]]
            base_folder_generator: Iterator[Traversable]
            parents: list[str]
            file_name_pkg: str
            stem: str
            suffixes: Sequence[str]
            suffix: str
            is_filter_suffix: bool
            is_filter_file_stem: bool
            path_out: Path

        d_files = {}

        # Fallback package folder
        if path_relative_package_dir is None:
            path_relative_package_dir = self.package_data_folder_start
        else:  # pragma: no cover
            pass

        # path_relative_package_dir no longer None
        if is_ok(path_relative_package_dir) and path_relative_package_dir not in (".",):
            # Any str will work
            path_relative_to = Path(path_relative_package_dir)
        elif issubclass(type(path_relative_package_dir), PurePath):
            path_relative_to = path_relative_package_dir
        else:
            # Unsupported type --> Fallback folder
            path_relative_to = self.package_data_folder_start

        # Callable check?!
        if cb_suffix is None or cb_file_stem is None:
            # Query is invalid; required args. ValueError??
            return d_files

        base_folder_generator = self.package_data_folders(
            cb_suffix=cb_suffix,
            cb_file_stem=cb_file_stem,
            path_relative_package_dir=path_relative_to,
        )
        lst_base_folders = list(base_folder_generator)
        is_generator_empty = len(lst_base_folders) == 0
        if is_generator_empty:
            # Query for package data files produced no results
            return d_files
        else:  # pragma: no cover
            pass

        # generator previously exhausted, refresh generator
        base_folder_generator = self.package_data_folders(
            cb_suffix=cb_suffix,
            cb_file_stem=cb_file_stem,
            path_relative_package_dir=path_relative_to,
        )

        # parent count is positive int
        if (
            parent_count is None
            or not isinstance(parent_count, int)
            or (isinstance(parent_count, int) and parent_count <= 0)
        ):
            d_files = {}
            return d_files

        parents = []
        for traversable_dir in base_folder_generator:
            for traversable_x in traversable_dir.iterdir():
                if not traversable_x.is_file():  # pragma: no cover
                    continue
                else:
                    # Filter out files not interested in
                    file_name_pkg = traversable_x.name
                    stem = msg_stem(file_name_pkg)
                    suffixes = Path(file_name_pkg).suffixes
                    suffix = "".join(suffixes)
                    is_filter_suffix = cb_suffix is None or cb_suffix(suffix)
                    is_filter_file_stem = cb_file_stem is None or cb_file_stem(stem)
                    if (
                        not is_filter_suffix or not is_filter_file_stem
                    ):  # pragma: no cover Filtered these
                        continue
                    else:
                        # extract -- filtered
                        with importlib_resources.as_file(traversable_x) as path_f:
                            parents.clear()
                            # Trigger LookupError -- No such package data folder
                            try:
                                path_out = self.path_relative(
                                    path_f,
                                    path_relative_package_dir=path_relative_to,
                                    parent_count=parent_count,
                                )
                            except LookupError:
                                """While extracting package data, files
                                exist, but folder doesn't match

                                Not a result, do not add to dict
                                """
                                pass
                            else:
                                # Successful search hit
                                # Remove file name from relative path
                                if str(path_out) == path_f.name:
                                    d_files[path_f.name] = ()
                                else:
                                    d_files[str(path_out)] = path_out.parts[:-1]

        return d_files

    def package_data_folders(
        self,
        *,
        cb_suffix=None,
        cb_file_stem=None,
        path_relative_package_dir=None,
    ):
        """Generic generator for retrieving package data folder paths. Does
        not do the file extraction.

        .. caution:: Generators delayed execution

           Creating a generator will always succeed; the code
           is not immediately executed. If the code, would normally
           raise an Exception, have to execute the generator for
           that to occur.

           This function is used as input to functions:
           :py:func:`PackageResource.resource_extract <logging_strict.util.package_resource.PackageResource.resource_extract>`
           or
           :py:func:`PackageResource.cache_extract <logging_strict.util.package_resource.PackageResource.cache_extract>`.
           So any Exception or logging would be delayed until those calls

        :param cb_suffix:

           Function creating using :py:func:`functools.partial` which
           filters by suffix

        :type cb_suffix: collections.abc.Callable[[str],bool]
        :param cb_file_stem:

           Function creating using :py:func:`functools.partial` which
           filters by file name stem

        :type cb_file_stem: collections.abc.Callable[[str],bool]
        :param package_name:

           Default [app name]. Python3 has namespace. So a
           Distribution need not contain all packages which will share
           the same namespace. There maybe multiple gui implementations
           installed

        :type package_name: str
        :param path_relative_package_dir:

           package base folder to start the search

        :type path_relative_package_dir: pathlib.Path | str | None

        :returns:

           All py:class:`importlib.resources.abc.Traversable`
           paths. Possibly filtered by theme

        :rtype: collections.abc.Iterator[importlib.resources.abc.Traversable]
        :raises:

           - :py:exc:`ImportError` -- package not installed. Before
             introspecting package data, install package

        """
        if TYPE_CHECKING:
            msg_exc: str
            base_token: str
            path_adjusted: Path
            parts: Sequence[str]
            traversable_data_dir: Traversable | None
            traversable_x: Traversable

        # Check package installed (in virtual environment)
        if not is_package_exists(self.package):
            msg_exc = (
                f"package {self.package} not installed. Before "
                "introspecting package data, install package"
            )
            raise ImportError(
                msg_exc,
                name=self.package,
                path=g_module,
            )
        else:  # pragma: no cover
            pass

        # Enforce default, but not on empty string
        if path_relative_package_dir is None:
            path_relative_package_dir = self.package_data_folder_start
        else:  # pragma: no cover
            pass

        # Determine base token
        if is_ok(path_relative_package_dir):
            with suppress(Exception):
                path_orig = Path(path_relative_package_dir)
                if not path_orig.is_absolute():
                    base_token = Path(path_relative_package_dir).parts[0]
                    path_adjusted = path_orig.relative_to(base_token)
                else:
                    # Do not assume ``data/``. Absolute path is ignored
                    base_token = None
                    path_adjusted = None
        elif (
            path_relative_package_dir is not None
            and issubclass(type(path_relative_package_dir), PurePath)
            and not path_relative_package_dir.is_absolute()
        ):
            base_token = path_relative_package_dir.parts[0]
            path_adjusted = path_relative_package_dir.relative_to(base_token)
        else:
            # Do not assume data/
            base_token = None
            path_adjusted = None

        """At this point know for certain package in virtual environment.
        Start folder, either exists or it doesn't. Adjust if it exists"""
        if base_token is not None:
            # Data folder *might* exist in package
            traversable_data_dir = _get_package_data_folder(
                f"{self.package}.{base_token}",
            )
            is_use_fallback = traversable_data_dir is None
        else:  # pragma: no cover
            # Module definity exists in virtual environment
            is_use_fallback = True

        if is_use_fallback is True:
            traversable_data_dir = _get_package_data_folder(self.package)
        else:  # pragma: no cover
            pass

        # Impossible --> traversable_data_dir is None
        if path_adjusted is None:  # pragma: no cover Is package base folder
            pass
        else:
            parts = path_adjusted.parts
            if len(parts) != 0:
                traversable_data_dir.joinpath(*parts)
            else:  # pragma: no cover
                pass

        # Check the root folder
        #    root is ``data``. root relative to ``data`` is ````
        if (
            len(
                list(
                    check_folder(
                        traversable_data_dir,
                        cb_suffix=cb_suffix,
                        cb_file_stem=cb_file_stem,
                    )
                )
            )
            != 0
        ):
            yield from check_folder(
                traversable_data_dir,
                cb_suffix=cb_suffix,
                cb_file_stem=cb_file_stem,
            )

        # Within traversable_root_dir, yield all other folders
        for traversable_x in walk_tree_folders(traversable_data_dir):
            yield from check_folder(
                traversable_x,
                cb_suffix=cb_suffix,
                cb_file_stem=cb_file_stem,
            )
        yield from ()

    def resource_extract(
        self,
        base_folder_generator,
        path_dest,
        /,
        cb_suffix=None,
        cb_file_stem=None,
        is_overwrite=False,
        as_user=False,
    ):
        """A generic extractor

        :menuselection:`package data --> dest folder`

        Use task specific resource extractors for a cleaner UX

        :param base_folder_generator:

           Package data folder Generator. Narrows down the search to
           folders known to contain target package data files

        :type base_folder_generator:

           collections.abc.Iterator[importlib.resources.abc.Traversable]

        :param path_dest: destination folder
        :type path_dest: pathlib.Path | str
        :param cb_suffix:

           Function creating using :py:func:`functools.partial` which
           filters by suffix

        :type cb_suffix: collections.abc.Callable[[str],bool]
        :param cb_file_stem:

           Function creating using :py:func:`functools.partial` which
           filters by file name stem

        :type cb_file_stem: collections.abc.Callable[[str],bool]
        :param is_overwrite:

           Default ``False``. Force overwriting of destination file

        :type is_overwrite: bool | None
        :param as_user:

           Default ``False``. ``False`` dest file owner set to root.
           Otherwise dest file owner set to user

        :type as_user: bool | None
        :returns: local cached file path
        :rtype: collections.abc.Iterator[pathlib.Path]

        .. seealso::

           :menuselection:`Generator --> Resource folders`
           :py:func:`PackageResource.package_data_folders <logging_strict.util.package_resource.PackageResource.package_data_folders>`

           cb_suffix
           :py:func:`~logging_strict.util.package_resource.filter_by_suffix`

        .. caution:: Refresh generator

           Resources will not be extracted if the generator is
           exhausted. If running in a loop, reinitialize generator

        .. todo:: acl permissions of dest folder

           Check acl writable permissions
           Is dest folder tree writable?


        """
        if TYPE_CHECKING:
            path_default: Path
            traversable_dir: Traversable
            traversable_x: Traversable
            file_name_pkg: str
            suffix: str
            is_filter_suffix: bool
            path_dest_file: Path
            is_ok_inner: bool

        operation = "resource_extract"

        # Positional arg
        if is_ok(path_dest):
            try:
                path_dest_dir = Path(path_dest)
            except Exception:  # pragma: no cover How to trigger?
                path_dest_dir = path_default
        elif path_dest is not None and issubclass(type(path_dest), PurePath):
            path_dest_dir = path_dest
        else:  # pragma: no cover
            yield from ()
            return

        # Informational -- after user input handling
        if is_module_debug:  # pragma: no cover
            msg_info = f"path_dest: {path_dest_dir}"
            print(msg_info, file=sys.stderr)
        pass

        # dest (base) folder
        # On Windows, prevent FileNotFound for Cache folder. Windows needs parents=True?
        if not path_dest_dir.exists():
            path_dest_dir.mkdir(
                mode=0o755,
                parents=True,
                exist_ok=True,
            )
            IsRoot.set_owner_as_user(
                path_dest_dir,
                is_as_user=as_user,
            )

        # Check acl writable permissions. Is dest folder tree writable?
        pass

        """ if package not installed,
        :paramref:`~logging_strict.util.package_resource.PackageResource.resource_extract.params.base_folder_generator`
        will raise :py:exc:`ImportError`
        """
        try:
            for traversable_dir in base_folder_generator:
                if traversable_dir.is_dir():  # pragma: no cover
                    dir_current_name = traversable_dir.name
                else:  # pragma: no cover
                    pass

                for traversable_x in traversable_dir.iterdir():
                    if traversable_x.is_file():
                        if is_module_debug:  # pragma: no cover
                            print(
                                f"dir {dir_current_name} file {traversable_x.name}",
                                file=sys.stderr,
                            )
                        file_name_pkg = traversable_x.name
                        stem = msg_stem(file_name_pkg)
                        suffixes = Path(file_name_pkg).suffixes
                        suffix = "".join(suffixes)
                        is_filter_suffix = cb_suffix is None or cb_suffix(suffix)
                        is_filter_file_stem = cb_file_stem is None or cb_file_stem(stem)
                        if is_filter_suffix and is_filter_file_stem:
                            # extract
                            with importlib_resources.as_file(
                                traversable_x
                            ) as path_entry:
                                """Get relative (to start dir) parent
                                folders (of package data file), so can extract, preserving
                                folder tree
                                """
                                pass

                                """
                                package start folder. Not:

                                - current folder

                                - relative folder
                                """
                                pkg_start_dir = self.package_data_folder_start
                                path_relative_to_base = self.path_relative(
                                    path_entry,
                                    parent_count=None,  # means get all
                                    path_relative_package_dir=pkg_start_dir,
                                )

                                # Strip the file name
                                tuple_relative_folders = path_relative_to_base.parts[
                                    :-1
                                ]

                                if is_module_debug:  # pragma: no cover
                                    print(
                                        f"path_relative_to_base {path_relative_to_base}",
                                        file=sys.stderr,
                                    )
                                    print(
                                        f"tuple_relative_folders {tuple_relative_folders}",
                                        file=sys.stderr,
                                    )
                                # Gracefully :py:meth:`Path.mkdir` dest folders
                                if len(tuple_relative_folders) != 0:
                                    """In dest folder, gracefully create all
                                    needed sub-folders. Setting correct owner
                                    along the way.
                                    So this script can be run as root,
                                    but the folders would be owned by
                                    normal session user
                                    """
                                    for num in range(0, len(tuple_relative_folders)):
                                        lst_folder = tuple_relative_folders[: num + 1]
                                        path_parent_tmp = path_dest_dir.joinpath(
                                            *lst_folder
                                        )
                                        path_parent_tmp.mkdir(
                                            mode=0o755,
                                            parents=False,
                                            exist_ok=True,
                                        )
                                        IsRoot.set_owner_as_user(
                                            path_parent_tmp,
                                            is_as_user=as_user,
                                        )
                                    path_dest_parent = path_dest_dir.joinpath(
                                        *tuple_relative_folders,
                                    )
                                else:
                                    path_dest_parent = path_dest_dir
                                path_dest_file = path_dest_parent.joinpath(
                                    path_entry.name,
                                )

                                if not path_dest_file.exists():
                                    is_ok_inner = True
                                else:
                                    if (
                                        not path_dest_file.is_file()
                                    ):  # pragma: no cover logs warning
                                        # Won't be able to overwrite existing fs object
                                        msg_warn = (
                                            f"In {operation}, destination "
                                            "exists, but is not a file. "
                                            "Can't overwrite. "
                                            f"{path_dest_file}"
                                        )
                                        _LOGGER.warning(msg_warn)
                                        is_ok_inner = False
                                    else:
                                        if (
                                            isinstance(is_overwrite, bool)
                                            and is_overwrite is True
                                        ):
                                            # overwrite existing file
                                            is_ok_inner = True
                                        else:
                                            # Not a file or don't overwrite
                                            is_ok_inner = False
                                """ The docs of shutil, pathlib, and os doesn't
                                    cover which Exceptions are raised. Even the
                                    source code isn't perfect. So best effort
                                """
                                try:
                                    if (
                                        not is_ok_inner
                                    ):  # pragma: no cover Don't overwrite
                                        pass
                                    else:
                                        """Compare sizes. timestamps
                                        better. Like GNU Makefile
                                        """
                                        if (
                                            path_dest_file.exists()
                                            and path_dest_file.is_file()
                                        ):
                                            dest_size = path_dest_file.stat().st_size
                                            src_size = path_entry.stat().st_size
                                            is_size_differs = dest_size != src_size
                                            if is_size_differs:
                                                # chown?!
                                                if is_module_debug:  # pragma: no cover
                                                    print(
                                                        f"copy (overwrites) {path_entry} --> {path_dest_file}",
                                                        file=sys.stderr,
                                                    )
                                                shutil.copy2(path_entry, path_dest_file)
                                                path_dest_file.chmod(0o644)
                                                IsRoot.set_owner_as_user(
                                                    path_dest_file,
                                                    is_as_user=as_user,
                                                )
                                            else:  # pragma: no cover Same size do nothing
                                                pass
                                        else:
                                            # chown?!
                                            if is_module_debug:  # pragma: no cover
                                                print(
                                                    f"copy (new) {path_entry} --> {path_dest_file}",
                                                    file=sys.stderr,
                                                )
                                            shutil.copy2(
                                                path_entry,
                                                path_dest_file,
                                            )
                                            path_dest_file.chmod(0o644)
                                            IsRoot.set_owner_as_user(
                                                path_dest_file,
                                                is_as_user=as_user,
                                            )
                                except (
                                    shutil.SameFileError
                                ):  # pragma: no cover logs warning
                                    # Attempted to copy file onto itself
                                    msg_warn = (
                                        "During resource extract, attempted "
                                        "to copy file onto itself. "
                                        f"{path_dest_file}"
                                    )
                                    _LOGGER.warning(msg_warn)
                                    yield from ()
                                except (
                                    FileNotFoundError
                                ):  # pragma: no cover logs warning
                                    # Dest folder does not exist
                                    msg_warn = (
                                        "During resource extract, destination "
                                        "folder does not exist "
                                        f"{path_dest_file}"
                                    )
                                    _LOGGER.warning(msg_warn)
                                    yield from ()
                                except (
                                    IsADirectoryError
                                ):  # pragma: no cover logs warning
                                    # Folder exists but not a folder!
                                    msg_warn = (
                                        "During resource extract, folder "
                                        "exists but not a folder! "
                                        f"{path_dest_file}"
                                    )
                                    _LOGGER.warning(msg_warn)
                                    yield from ()
                                except OSError:  # pragma: no cover logs warning
                                    # Problem copying file stats
                                    msg_warn = (
                                        "During resource extract, "
                                        "problem copying file stats "
                                        f"{path_dest_file}"
                                    )
                                    _LOGGER.warning(msg_warn)
                                    yield from ()
                                except PermissionError:  # pragma: no cover logs warning
                                    """Insufficient permissions. Cannot copy
                                    file or chmod
                                    """
                                    msg_warn = (
                                        "During resource extract, "
                                        "Insufficient permissions. Cannot "
                                        "copy file or chmod "
                                        f"{path_dest_file}"
                                    )
                                    _LOGGER.warning(msg_warn)
                                    yield from ()
                                else:
                                    if is_module_debug:  # pragma: no cover
                                        print(
                                            f"yielding {path_dest_file}",
                                            file=sys.stderr,
                                        )
                                    yield path_dest_file
        except ImportError:
            """package is not installed (in virtual
            environment)
            """
            str_tb = traceback.format_exc()
            _LOGGER.info(str_tb)
            msg_warn = (
                "Package is not installed. Tried to access package data "
                "within a non-existing package. Install it first "
            )
            _LOGGER.warning(msg_warn)
            yield from ()

    def cache_extract(
        self,
        base_folder_generator,
        /,
        cb_suffix=None,
        cb_file_stem=None,
        is_overwrite=False,
    ):
        """A generic extractor to local cache folder

        :menuselection:`package data --> cache folder`

        :param base_folder_generator:

           Package data folder Generator. Narrows down folders to
           search to only folders containing the target data files

        :type base_folder_generator:

           collections.abc.Iterator[importlib.resources.abc.Traversable]

        :param cb_suffix:

           Function creating using :py:func:`functools.partial` which
           filters by suffix

        :type cb_suffix: collections.abc.Callable[[str],bool]
        :param cb_file_stem:

           Function creating using :py:func:`functools.partial` which
           filters by file name stem

        :type cb_file_stem: collections.abc.Callable[[str],bool]
        :returns: local cached file path
        :rtype: collections.abc.Iterator[pathlib.Path]

        .. seealso::

           :py:func:`~logging_strict.util.package_resource.filter_by_suffix`

        .. caution:: Refresh generator

           Resources will not be extracted if the generator is
           exhausted. If running in a loop, reinitialize generator


        """
        # user local cache
        dest_path = _extract_folder(self.package)

        if is_module_debug:  # pragma: no cover
            print(f"cache_extract... {dest_path} {type(dest_path)}", file=sys.stderr)

        yield from self.resource_extract(
            base_folder_generator,
            dest_path,
            cb_suffix=cb_suffix,
            cb_file_stem=cb_file_stem,
            as_user=True,
        )
