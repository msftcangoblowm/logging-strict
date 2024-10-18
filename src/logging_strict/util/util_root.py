"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

..

Lets write this only once (DRY principle)

Returns messages thru callbacks. So do not print or log anything

**Module private variables**

.. py:data:: __all__
   :type: tuple[str, str]
   :value: ("IsRoot", "check_python_not_old")

   Module object exports

.. py:data:: g_module
   :type: str
   :value: "logging_strict.util.util_root"

   This module's dotted path

.. py:data:: _LOGGER
   :type: logging.Logger

   Module level logger

.. py:data:: g_is_root
   :type: bool

   ``True`` if app run as a service with root privledges. ``False`` if
   run normally and sanely

.. py:data:: is_python_old
   :type: bool

    ``True`` if py38- otherwise ``False``

**Module objects**

"""

import getpass
import logging
import os
import platform
import shutil
import sys
from pathlib import (
    Path,
    PurePath,
)
from typing import (
    TYPE_CHECKING,
    ClassVar,
)

from ..constants import g_app_name

if platform.system().lower() != "windows":  # pragma: no cover
    from pwd import getpwnam
else:  # pragma: no cover
    getpwnam = None

__all__ = (
    "IsRoot",
    "check_python_not_old",
)

g_module = f"{g_app_name}.util.util_root"
_LOGGER = logging.getLogger(g_module)

is_python_old = sys.version_info < (3, 9)

if TYPE_CHECKING:
    if sys.version_info >= (3, 9):  # pragma: no cover
        from collections.abc import Callable  # noqa: F401 Used by sphinx
    else:  # pragma: no cover
        from typing import Callable  # noqa: F401 Used by sphinx


def is_user_admin():  # pragma: no cover
    """Detect if running with elevated permissions

    The inner function fails unless you have Windows XP SP2 or
    higher. The failure causes a traceback to be printed and this
    function to return False.

    :returns: True if the script run as root otherwise False
    :rtype: bool

    .. seealso::

       https://stackoverflow.com/questions/19672352/how-to-run-script-with-elevated-privilege-on-windows
       https://gist.github.com/sylvainpelissier/ff072a6759082590a4fe8f7e070a4952

    """
    if platform.system().lower() == "windows":
        import ctypes
        import traceback

        # WARNING: requires Windows XP SP2 or higher!
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except Exception:
            traceback.print_exc()
            msg_info = "Admin check failed, assuming not an admin."
            _LOGGER.info(msg_info)
            return False
    else:
        # Check for root on Posix
        return os.getuid() == 0


g_is_root = is_user_admin()


def get_logname():
    """The service to be run as root.
    The systray app will be run as Linux session user.

    Regardless if called by the service or the systray app,
    retrieve the logname

    :py:meth:`FStab.__get_guid` and
    :py:meth:`os.getlogin` are equivalent. ``__get_guid`` requires a
    subprocess call.

    Issue with :py:meth:`os.getlogin`:

       Source/Credit
       `Christian Heimes <https://bugs.python.org/issue40821>`_

       ERRNO 6:
       ENXIO The calling process has no controlling terminal

    :py:meth:`os.getlogin` returns the name of the user logged in
    on the controlling terminal of the process. Typically processes
    in user session (tty, X session) have a controlling terminal.

    Service processes usually do not have a controlling terminal.
    These are spawned by a service manager, like: initd, systemd,
    openrc, runit, upstart, ...

    Have to get the user information by other means. Documentation
    for :py:meth:`os.getlogin` recommends
    :py:meth:`getpass.getuser`.

    :returns: current session user name
    :rtype: str
    """
    if TYPE_CHECKING:
        ret: str

    ret = getpass.getuser()
    if ret == "root":  # pragma: no cover
        ret = os.getlogin()
    else:  # pragma: no cover
        pass

    return ret


def ungraceful_app_exit():  # pragma: no cover
    """Code separated, so it can be Mock'ed to do nothing"""
    if TYPE_CHECKING:
        exit_code: int

    exit_code = 2
    sys.exit(exit_code)


class IsRoot:
    """Checks whether or not root
    DRY principle; don't repeat yourself; which became tiresome

    Class variables

    :cvar __slots__: Turns off dynamic instance variables
    :vartype: ClassVar[tuple[()]]

    """

    if TYPE_CHECKING:
        __slots__: ClassVar[tuple[()]]

    __slots__ = ()

    @staticmethod
    def is_root():
        """Whether or not root.

        :returns: ``True`` is root otherwise ``False``
        :rtype: bool
        """
        return g_is_root

    @classmethod
    def path_home_root(cls):
        """Replacement for get_logname

        Intended to be run only by root, but not necessarily

        :returns: root home folder
        :rtype: pathlib.Path
        """
        if TYPE_CHECKING:
            is_not_root: bool
            logname: str

        is_not_root = not g_is_root
        logname = getpass.getuser()
        return Path("/root") if is_not_root else Path(f"/{logname}")

    @classmethod
    def check_root(
        cls,
        callback=None,
        is_app_exit=False,
        is_raise_exc=False,
    ):
        """What to do if app executed as root

        :param callback:

           If provided passes error message for handling

        :type callback: collections.abc.Callable[[], str] | None
        :param is_app_exit: True and not root, should exit app
        :type is_app_exit: bool | None
        :param is_raise_exc:

           True and not root, should raise an Exception

        :type is_raise_exc: bool | None

        :raises:

           :py:exc:`PermissionError` -- Requires root to run


        """
        if TYPE_CHECKING:
            msg_warn: str

        if is_app_exit is None:
            is_app_exit = False
        elif not isinstance(is_app_exit, bool):
            is_app_exit = False
        else:  # pragma: no cover Do Nothing
            pass

        if is_raise_exc is None:
            is_raise_exc = False
        elif not isinstance(is_raise_exc, bool):
            is_raise_exc = False
        else:  # pragma: no cover Do Nothing
            pass

        try:
            assert g_is_root
        except AssertionError as e:
            msg_warn = "Requires root to run"
            if callback is not None:
                callback(msg_warn)
            if is_app_exit is True:  # pragma: no cover No way to test
                ungraceful_app_exit()
            elif is_raise_exc is True:
                raise PermissionError(msg_warn) from e
            else:
                pass

    @classmethod
    def check_not_root(
        cls,
        callback=None,
        is_app_exit=False,
        is_raise_exc=False,
    ):
        """What to do if app executed as normal user

        :param callback:

           If provided passes error message for handling

        :type callback: collections.abc.Callable[[], str] | None
        :param is_app_exit:

           True and not normal user, should exit app

        :type is_app_exit: bool | None
        :param is_raise_exc:

           True and not normal user, should raise an Exception

        :type is_raise_exc: bool | None

        :raises:

           :py:exc:`PermissionError` -- Requires root to run


        """
        if TYPE_CHECKING:
            msg_warn: str

        if is_app_exit is None:
            is_app_exit = False
        elif not isinstance(is_app_exit, bool):
            is_app_exit = False
        else:  # pragma: no cover
            pass

        if is_raise_exc is None:
            is_raise_exc = False
        elif not isinstance(is_raise_exc, bool):
            is_raise_exc = False
        else:  # pragma: no cover
            pass

        try:
            assert not g_is_root
        except AssertionError as e:
            msg_warn = "Not run as root. Executed by session user"
            if callback is not None:
                callback(msg_warn)
            else:  # pragma: no cover
                pass

            if is_app_exit is True:
                ungraceful_app_exit()
            elif is_raise_exc is True:
                raise PermissionError(msg_warn) from e
            else:  # pragma: no cover
                pass

    @classmethod
    def set_owner_as_user(
        cls,
        path_file,
        is_as_user=False,
    ):
        """
        :param path_file: Path to the file
        :type path_file: typing.Any
        :param is_as_user:

           Flag. ``True`` if file permissions should be as a user otherwise ``False``

        :type is_as_user: typing.Any | None
        """
        if TYPE_CHECKING:
            session_user_name: str
            session_uid: int
            session_gid: int

        if (
            path_file is not None
            and isinstance(path_file, str)
            and len(path_file) != 0
            and path_file != "."
        ):
            path_file = Path(path_file)
        elif issubclass(type(path_file), PurePath):
            pass
        else:
            return None

        if not path_file.exists() or not path_file.is_file():
            return None

        if is_as_user is None:
            is_as_user = False
        elif not isinstance(is_as_user, bool):
            is_as_user = False
        else:  # pragma: no cover
            pass

        if g_is_root and is_as_user is True and platform.system().lower() != "windows":
            # https://stackoverflow.com/questions/8086412/howto-determine-file-owner-on-windows-using-python-without-pywin32
            session_user_name = get_logname()
            session_uid = getpwnam(session_user_name)[2]
            session_gid = getpwnam(session_user_name)[3]
            shutil.chown(
                path_file,
                user=session_uid,
                group=session_gid,
            )
        else:  # pragma: no cover Do nothing
            pass


def check_python_not_old(
    callback=None,
    is_app_exit=False,
    is_raise_exc=False,
):
    """Warn raising error if python interpretor version is an
    unsupported version

    :param callback:

       If provided passes error message for handling

    :type callback: collections.abc.Callable[[], str] | None
    :param is_app_exit: True and before py39, should exit app
    :type is_app_exit: bool | None
    :param is_raise_exc:
       True and before py39, should raise an Exception

    :type is_raise_exc: bool | None

    :raises:

       :py:exc:`PermissionError` -- Requires root to run


    """
    if TYPE_CHECKING:
        major: str
        minor: str
        patch: str
        current_version: str
        msg_warn: str

    if is_app_exit is None:
        is_app_exit = False
    elif not isinstance(is_app_exit, bool):
        is_app_exit = False
    else:  # pragma: no cover
        pass

    if is_raise_exc is None:
        is_raise_exc = False
    elif not isinstance(is_raise_exc, bool):
        is_raise_exc = False
    else:  # pragma: no cover
        pass

    try:
        assert not is_python_old
    except AssertionError as e:
        major, minor, patch = platform.python_version_tuple()
        current_version = f"{g_app_name} {major}.{minor}.{patch}"
        msg_warn = (
            "Requires Python version 3.9 or later. Python version: "
            f"{current_version}"
        )
        if callback is not None:
            callback(msg_warn)
        if is_app_exit:
            ungraceful_app_exit()
        elif is_raise_exc:
            raise PermissionError(msg_warn) from e
