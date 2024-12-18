"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

..

Get XDG user or site folders

Some platforms require app author name. Linux doesn't.

Take the (head) author name from the target package's meta data and then slugify
it. If that gives a wrong result, on a per author basis, would need a way
to specify the correct author name

Since the target platform is POSIX, not losing sleep over this issue

**Module private variables**

.. py:data:: __all__
   :type: tuple[str, str, str]
   :value: ("DestFolderSite", "DestFolderUser", "_get_path_config")

   Module exports

**Module objects**

"""

from __future__ import annotations

import email
import email.policy
from importlib import metadata
from pathlib import Path

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
):
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
    """XDG Site folders

    :ivar appname: Package name
    :vartype appname: str
    :ivar author_no_period:

       Default ``True``. ``True`` if should remove period from author
       name otherwise ``False``

    :vartype author_no_period: str
    :ivar author_no_space:

       Default ``True``. ``True`` if should remove whitespace from author
       name otherwise ``False``

    :vartype author_no_space: str
    :ivar author_no_underscore:

       Default ``True``. ``True`` if should remove underscore from author
       name otherwise ``False``

    :vartype author_no_underscore: str
    :ivar version:

       Default ``None``. Possible to have version specific author
       information. Can specific version

    :vartype version: str | None
    :ivar multipath:

       Default ``False``. Could retrieve all possible folders.
       ``True`` for multipath. ``False`` for first entry in multipath

    :vartype multipath: bool | None
    """

    def __init__(
        self,
        appname,
        author_no_period=True,
        author_no_space=True,
        author_no_underscore=True,
        version=None,
        multipath=False,
    ):
        """Class constructor"""
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
    def data_dir(self):
        """Get XDG site data dir

        :returns: XDG site data dir
        :rtype: str
        """
        return AppDirs(
            appname=self.appname,
            appauthor=self.appauthor,
            version=self.version,
            multipath=self.multipath,
        ).site_data_dir

    @property
    def config_dir(self):
        """Get XDG site config dir

        :returns: XDG site config dir
        :rtype: str
        """
        return AppDirs(
            appname=self.appname,
            appauthor=self.appauthor,
            version=self.version,
            multipath=self.multipath,
        ).site_config_dir


class DestFolderUser:
    """XDG User folders

    :ivar appname: Package name
    :vartype appname: str
    :ivar author_no_period:

       Default ``True``. ``True`` if should remove period from author
       name otherwise ``False``

    :vartype author_no_period: str
    :ivar author_no_space:

       Default ``True``. ``True`` if should remove whitespace from author
       name otherwise ``False``

    :vartype author_no_space: str
    :ivar author_no_underscore:

       Default ``True``. ``True`` if should remove underscore from author
       name otherwise ``False``

    :vartype author_no_underscore: str
    :ivar version:

       Default ``None``. Possible to have version specific author
       information. Can specific version

    :vartype version: str | None
    :ivar roaming:

       Default ``False``. Only applicable to Windows

    :vartype roaming: bool | None
    :ivar opinion:

       Default ``True``. ??

    :vartype opinion: bool | None
    """

    def __init__(
        self,
        appname: str,
        author_no_period=True,
        author_no_space=True,
        author_no_underscore=True,
        version=None,
        roaming=False,
        opinion=True,
    ):
        """Class constructor"""
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
    def data_dir(self):
        """Get XDG user data dir

        :returns: XDG user data dir
        :rtype: str
        """
        return AppDirs(
            appname=self.appname,
            appauthor=self.appauthor,
            version=self.version,
            roaming=self.roaming,
        ).user_data_dir

    @property
    def config_dir(self):
        """Get XDG user config dir

        :returns: XDG user config dir
        :rtype: str
        """
        return AppDirs(
            appname=self.appname,
            appauthor=self.appauthor,
            version=self.version,
            roaming=self.roaming,
        ).user_config_dir

    @property
    def cache_dir(self):
        """Get XDG user cache dir

        :returns: XDG user cache dir
        :rtype: str
        """
        return user_cache_dir(
            appname=self.appname,
            appauthor=self.appauthor,
            version=self.version,
            opinion=self.opinion,
        )

    @property
    def state_dir(self):
        """Get XDG user state dir

        :returns: XDG user state dir
        :rtype: str
        """
        return AppDirs(
            appname=self.appname,
            appauthor=self.appauthor,
            version=self.version,
            roaming=self.roaming,
        ).user_state_dir

    @property
    def log_dir(self):
        """Get XDG user log dir

        :returns: XDG user log dir
        :rtype: str
        """
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
):
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
    :rtype: pathlib.Path
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
