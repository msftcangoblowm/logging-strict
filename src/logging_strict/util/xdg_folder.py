"""
.. py:module:: logging_strict.util.xdg_folder
   :platform: Unix
   :synopsis: Get XDG user or site folders

.. moduleauthor:: Dave Faulkmore <faulkmore telegram>

..

Get XDG user or site folders

Some platforms require app author name. Linux doesn't.

Take the (head) author name from the target package's meta data and then slugify
it. If that gives a wrong result, on a per author basis, would need a way
to specify the correct author name

Since the target platform is POSIX, not losing sleep over this issue

"""
import email
import email.policy
from importlib import metadata
from pathlib import Path
from typing import Optional

from appdirs import (
    AppDirs,
    user_cache_dir,
    user_log_dir,
)

from .check_type import is_not_ok

__all__ = ("DestFolderSite", "DestFolderUser", "_get_path_config")


def _get_author(
    package,
    no_period=True,
    no_space=True,
    no_underscore=True,
) -> str:
    """Affects Windows and MacOS platforms. Linux ignores package
    (head) author name.

    There is no standard for author names. On the affected
    platforms more often than not it's a company name, not a persons.

    Don't use those platforms, so have no good solution to this problem.
    Nor will lose any sleep over this

    :param package:

       Default :paramref:`g_app_name`. Target package to retrieve author name.
       The default is useless, **always** provide the target package

    :type package: str
    :param no_period: Default ``True``. If ``True`` removes period
    :type no_period: bool
    :param no_space: Default ``True``. If ``True`` replaced with hyphen
    :type no_space: bool
    :param no_underscore: Default ``True``. If ``True`` replaced with hyphen
    :type no_underscore: bool
    :returns: author name modified on a per author basis
    :rtype: str

    .. seealso::

       `Parse Author-email <https://stackoverflow.com/a/75803208>`_

       `appdirs <https://pypi.org/project/appdirs/>`_

    """
    email_msg = metadata.metadata(package)
    addresses = email_msg["Author-email"]
    em = email.message_from_string(
        f"To: {addresses}",
        policy=email.policy.default,
    )
    author_head = em["to"].addresses[0].display_name

    """
    package: appdirs

    In setup.py,
    .. code-block:: text

       author='Trent Mick',
       author_email='trentm@gmail.com',

    """
    if is_not_ok(author_head):
        author_raw = email_msg["Author"]
        author_head = author_raw
    else:  # pragma: no cover
        pass

    # strictyaml
    # Colm O'Connor --> Colm OConnor
    author_head = author_head.replace("'", "")

    # typing-extensions
    # Guido van Rossum, Jukka Lehtosalo, Łukasz Langa, Michael Lee
    author_head = author_head.replace(", ", "-")

    if no_period is True:
        author_head = author_head.replace(".", "")
    else:  # pragma: no cover
        pass

    if no_space is True:
        author_head = author_head.replace(" ", "-")
    else:  # pragma: no cover
        pass

    if no_underscore is True:
        author_head = author_head.replace("_", "-")
    else:  # pragma: no cover
        pass

    return author_head


class DestFolderSite:
    def __init__(
        self,
        appname: str,
        author_no_period=True,
        author_no_space=True,
        author_no_underscore=True,
        version: Optional[str] = None,
        multipath: Optional[bool] = False,
    ) -> None:
        self.appname = appname
        self.appauthor = _get_author(
            appname,
            no_period=author_no_period,
            no_space=author_no_space,
            no_underscore=author_no_underscore,
        )
        self.version = version
        self.multipath = multipath

    @property
    def data_dir(self) -> str:
        return AppDirs(
            appname=self.appname,
            appauthor=self.appauthor,
            version=self.version,
            multipath=self.multipath,
        ).site_data_dir

    @property
    def config_dir(self) -> str:
        return AppDirs(
            appname=self.appname,
            appauthor=self.appauthor,
            version=self.version,
            multipath=self.multipath,
        ).site_config_dir


class DestFolderUser:
    def __init__(
        self,
        appname: str,
        author_no_period=True,
        author_no_space=True,
        author_no_underscore=True,
        version: Optional[str] = None,
        roaming: Optional[bool] = False,
        opinion: Optional[bool] = True,
    ) -> None:
        self.appname = appname
        self.appauthor = _get_author(
            appname,
            no_period=author_no_period,
            no_space=author_no_space,
            no_underscore=author_no_underscore,
        )
        self.version = version
        self.roaming = roaming
        self.opinion = opinion

    @property
    def data_dir(self) -> str:
        return AppDirs(
            appname=self.appname,
            appauthor=self.appauthor,
            version=self.version,
            roaming=self.roaming,
        ).user_data_dir

    @property
    def config_dir(self) -> str:
        return AppDirs(
            appname=self.appname,
            appauthor=self.appauthor,
            version=self.version,
            roaming=self.roaming,
        ).user_config_dir

    @property
    def cache_dir(self) -> str:
        return user_cache_dir(
            appname=self.appname,
            appauthor=self.appauthor,
            version=self.version,
            opinion=self.opinion,
        )

    @property
    def state_dir(self) -> str:
        return AppDirs(
            appname=self.appname,
            appauthor=self.appauthor,
            version=self.version,
            roaming=self.roaming,
        ).user_state_dir

    @property
    def log_dir(self) -> str:
        return user_log_dir(
            appname=self.appname,
            appauthor=self.appauthor,
            version=self.version,
            opinion=self.opinion,
        )


def _get_path_config(
    package,
    author_no_period=True,
    author_no_space=True,
    author_no_underscore=True,
    version=None,
    roaming=False,
) -> Path:
    """Mockable module level function. Gets the user
    data folder, not the user config folder

    :param package: Target package, might not be ur package!
    :type package: str
    :param author_no_period: Default ``True``. If ``True`` removes period
    :type author_no_period: bool
    :param author_no_space: Default ``True``. If ``True`` replaced with hyphen
    :type author_no_space: bool
    :param author_no_underscore: Default ``True``. If ``True`` replaced with hyphen
    :type author_no_underscore: bool
    :returns: user data folder Path
    :rtype: :py:class:`~pathlib.Path`
    """
    str_user_data_dir = DestFolderUser(
        package,
        author_no_period=author_no_period,
        author_no_space=author_no_space,
        author_no_underscore=author_no_underscore,
        version=version,
        roaming=roaming,
    ).data_dir
    ret = Path(str_user_data_dir)

    return ret
