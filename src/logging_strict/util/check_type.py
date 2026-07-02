"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

Check utility functions

"""

from pathlib import (
    Path,
    PurePath,
)

__all__ = (
    "check_type_path",
    "is_not_ok",
    "is_ok",
    "check_int_verbosity",
    "check_start_folder_importable",
)


def check_type_path(module_path, *, msg_context=None):
    """Check
    :py:obj:`logging_strict.util.check_type.check_type_path.params.module_path`
    is a :py:class:`~pathlib.Path`

    :param module_path:

       Parameter to check, if possible and necessary, coerse into
       :py:class:`~pathlib.Path`

    :type module_path: typing.Any | None
    :param msg_additional:

       Context specific message, **not** concerning type

    :type msg_additional: str | None
    :returns: Parameter coersed to :py:class:`~pathlib.Path`
    :rtype: pathlib.Path
    :raises:

       - :py:exc:`TypeError` -- Invalid type. :py:class:`~pathlib.Path`
         or PathLike expected

       - :py:exc:`ValueError` -- Cannot expand session user home folder
         or path is invalid

    """
    msg_type_error = f"Path or PathLike expected, got {module_path!r}"
    msg_expanduser = "Home directory can’t be resolved"
    msg_supplimentary = msg_context if is_ok(msg_context) else ""
    # neither non-empty str nor Path
    if module_path is None or not (
        (isinstance(module_path, str) and bool(module_path.strip()))
        or issubclass(type(module_path), PurePath)
    ):  # pragma: no branch
        msg_exc = f"{msg_type_error} {msg_supplimentary}"
        raise TypeError(msg_exc)

    assert module_path is not None
    if isinstance(module_path, str):
        path_module = Path(module_path)
    else:
        path_module = module_path

    try:
        """Do not know whether relative or absolute path, so no
        :py:func:`pathlib.Path.resolve`
        """
        path_absolute = path_module.expanduser()
    except (PermissionError, OSError, RuntimeError, Exception) as e:
        # str path is not a path, contains nonsense characters
        # home folder can't be resolved. Not mounted?
        msg_exc = f"{msg_expanduser}. Path: {module_path!r} {msg_supplimentary}"
        raise ValueError(msg_exc) from e

    return path_absolute


def is_not_ok(test):
    """Check not ``None``, not a str, or an empty str

    :param test: variable to test
    :type test: typing.Any | None
    :returns: ``True`` if either: ``None``, not a str, or an empty str
    :rtype: bool
    """
    is_str = test is not None and isinstance(test, str)
    if is_str:
        # is_really_empty
        ret = not bool(test.strip())
    else:
        # None or not a str
        ret = True

    return ret


def is_ok(test):
    """Check if non-empty str

    Edge case: contains only whitespace --> ``False``

    :param test: variable to test
    :type test: typing.Any | None
    :returns: ``True`` if non-empty str otherwise ``False``
    :rtype: bool
    """
    ret = test is not None and isinstance(test, str) and bool(test.strip())

    return ret


def check_int_verbosity(test):
    """Check verbosity is an integer with value either 1 or 2

    :param test: variable to test
    :type test: typing.Any | None
    :returns: ``True`` if integer 1 or 2 otherwise ``False``
    :rtype: bool
    """
    if test is None:
        ret = False
    else:
        if not isinstance(test, int):
            ret = False
        else:
            ret = test in (1, 2)

    return ret


def check_start_folder_importable(folder_start):
    """Folder containing tests, must have a ``__init__.py`` file. Super
    easy to forget. The required file, indicates the test folder is within
    a "**package**". Not having that file, unittest discover will
    ungraciously complain.

    To reproduce the issue, on a folder **not** containing a ``__init__.py`` file

    .. code-block:: shell

       python -m unittest discover -t . -s "tests/util" -p 'test_check_type*.py'

    :py:exc:`ImportError`: Start directory is not importable:
    '[top level folder absolute path]/tests/util'

    With the laughable and useless exit code 1. Exit code 1 and 2
    (insufficient permissions) indicates the coder hates you and doesn't care
    about UX.

    Have a searing hate for error messages that offer no suggestions on how to
    resolve the issue. Forcing a web search. Bad UX! BAD!! Also unnecessarily
    bleeds a traceback. Should produce only an exit code

    .. code-block:: shell

       python -m unittest discover --help

    Should contain a section, EXIT CODES, listing the exit codes with the
    message **and** suggestion on how to resolve the issue. Added benefit,
    the entrypoint becomes testable.
    Call the entrypoint in a subprocess and assert the return value(s)

    Did figure out why without a web search, but coulda just said,
    "Make a __init__.py" in that folder, touch [folder path]/__init__.py"

    :param folder_start: folder absolute path
    :type folder_start: typing.Any | None
    :returns:

       ``True`` if folder contains ``__init__.py`` file otherwise ``False``

    :rtype: bool
    :raises:

       - :py:exc:`TypeError` -- Unsupported type. Expected folder absolute path

       - :py:exc:`ValueError` -- Cannot expand session user home folder
         or path is invalid

       - :py:exc:`NotADirectoryError` -- Not a folder. Expected a folder absolute path

    """
    try:
        path_absolute_folder = check_type_path(folder_start)
    except (ValueError, TypeError):
        raise

    if not (
        path_absolute_folder.exists() and path_absolute_folder.is_dir()
    ):  # pragma: no branch
        msg_exc = (
            f"Not a folder: {path_absolute_folder}, check, in that "
            "folder, for __init__.py  would fail. Create the "
            "folder and __init__.py within that folder using touch command"
        )
        raise NotADirectoryError(msg_exc)

    if not path_absolute_folder.is_absolute():
        ret = False
    else:
        path_missing = path_absolute_folder.joinpath("__init__.py")
        if not path_missing.exists():
            ret = False
        else:
            # False is insane, but lets create a unittest for it anyways
            ret = path_missing.is_file()

    return ret
