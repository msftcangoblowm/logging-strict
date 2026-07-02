"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

Get XDG user or site folders.

MacOS, to avoid name possible app naming collisions, requires app author
name. If a package doesn't specify an app author, e.g. ``selenium``, the
code must specify it using class property, ``appauthor``.

``appauthor`` is normalized for use as a folder name.

If a package doesn't reveal the author, the appauthor is None.
The (relative) folder path becomes ``[appname]/None``. So coder should
use the class property setter, appauthor, to specify what they'd like
the appauthor to be.

Package ``platformdirs`` author unilaterally decided that appauthor
is unnecessary; that name collisions are rare enough to be a detail
better left out.

Contend that decision is not the ``platformdirs`` author to make.
If OS platform compatability is important then avoid ``platformdirs``.

Get XDG cache dir for typical package

.. testcode::

    from logging_strict.util.xdg_folder import DestFolderUser

    package = "appdirs"  # with author attribution
    xdg_user = DestFolderUser(package)
    assert isinstance(xdg_user.cache_dir, str)

Get XDG cache dir for package without author attribution

.. code-block:: text

    from logging_strict.util.xdg_folder import DestFolderUser

    package = "selenium"  # lacks author attribution
    xdg_user = DestFolderUser(package)
    xdg_user.appauthor = "John Doe"  # MacOS thanks you
    assert isinstance(xdg_user.cache_dir, str)

"""

import email
import email.policy
from pathlib import Path
from typing import TYPE_CHECKING

import importlib_metadata as metadata
from appdirs import (
    AppDirs,
    user_cache_dir,
    user_log_dir,
)

from .check_type import (
    is_not_ok,
    is_ok,
)

if TYPE_CHECKING:
    from collections.abc import Callable

__all__ = ("DestFolderSite", "DestFolderUser", "_get_path_config")


def _author_normalize(
    author_name,
    no_period=True,
    no_space=True,
    no_underscore=True,
):
    """Only normalize the author name, without retrieving it.
    Examples and how each is normalized:

    General principles

    - remove periods
    - underscore --> hyphen
    - single space --> hyphen

    strictyaml author

    - Colm O'Connor --> Colm-OConnor

    typing-extensions authors

    - Guido van Rossum, Jukka Lehtosalo, Łukasz Langa, Michael Lee

    Guido-van-Rossum-Jukka-Lehtosalo-Łukasz-Langa-Michael-Lee

    appdirs

    `selenium` package doesn't state an author. From POV of copyright
    law, this is mind blowing. How can have a license without an author?
    Whose granting those rights and do they actually have the authority to
    grant those rights? Is the cup half empty or half full?
    Are you confused yet?

    This is the reason for the appauthor class property. Rather than assuming
    there is one correct answer. Leave that for the coder to decide. So as not
    to deny coders the opportunity to become really pissed off at a package
    author's neglegence.

    :type author_name: str
    :param no_period: Default True
    :type no_period: bool
    :param no_space: Default True
    :type no_space: bool
    :param no_underscore: Default True
    :type no_underscore: bool
    :raises:

       - :py:exc:`TypeError` -- all args are required and must be correct type

    """
    if (
        author_name is None
        or not isinstance(author_name, str)
        or no_period is None
        or not isinstance(no_period, bool)
        or no_space is None
        or not isinstance(no_space, bool)
        or no_underscore is None
        or not isinstance(no_underscore, bool)
    ):  # pragma: no branch
        msg_warn = (
            f"All params are required. Got author {author_name!r} "
            f"no_period {no_period!r} no_space {no_space!r} "
            f"no_underscore {no_underscore!r}"
        )
        raise TypeError(msg_warn)

    # strictyaml
    # Colm O'Connor --> Colm OConnor
    name = author_name.replace("'", "")

    # typing-extensions
    # Guido van Rossum, Jukka Lehtosalo, Łukasz Langa, Michael Lee
    name = name.replace(", ", "-")

    if no_period:  # pragma: no branch
        name = name.replace(".", "")

    if no_space:  # pragma: no branch
        name = name.replace(" ", "-")

    if no_underscore:  # pragma: no branch
        name = name.replace("_", "-")

    return name


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

    package: appdirs
    In setup.py,

    .. code-block:: text

       author='Trent Mick',
       author_email='trentm@gmail.com',

    So author name can also be hidden within "Author-email" field.
    If not try "Author" then fallback is None. Which is useless, wrong,
    and crying out for the coder to make a judgement call!

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
    :rtype: str | None

    .. seealso::

       `Parse Author-email <https://stackoverflow.com/a/75803208>`_

       `appdirs <https://pypi.org/project/appdirs/>`_

    """

    def filter_author_email(addresses: str) -> str:
        """Filter (author) addresses field to get author name"""
        em = email.message_from_string(
            f"To: {addresses}",
            policy=email.policy.default,
        )
        author_head = em["to"].addresses[0].display_name
        return author_head

    def parse_name(
        email_msg: "metadata.PackageMetadata",
        field_name: str,
        cb_filter: "Callable[[str], str] | None" = None,
    ) -> "str | None":
        """From email_msg field get value and if applicable pass thru callback."""
        assert field_name is not None
        val = email_msg.get(field_name, None)
        ret_inner = None
        if val is not None and isinstance(val, str):
            if cb_filter is not None and callable(cb_filter):
                out_inner = cb_filter(val)
                # empty str if only email address and no display_name
                if out_inner.strip() != "":  # pragma: no branch
                    ret_inner = out_inner
            else:
                ret_inner = val

        return ret_inner

    ret_outer = None
    if is_ok(package):  # pragma: no branch
        email_msg = metadata.metadata(package)
        try_these = (
            ("Author-email", filter_author_email),
            ("Author", None),
        )
        for t_try in try_these:
            field_, cb_ = t_try
            out = parse_name(email_msg, field_, cb_)
            if ret_outer is None and out is not None:  # pragma: no cover
                ret_outer = _author_normalize(
                    out,
                    no_period=no_period,
                    no_space=no_space,
                    no_underscore=no_underscore,
                )

    return ret_outer


class XDGBase:
    """Shared UI to keep code DRY.

    :raises:

       - :py:exc:`ValueError` -- package name not provided. Cannot query
         for author name

    """

    __slots__ = (
        "_appauthor",
        "_no_period",
        "_no_space",
        "_no_underscore",
        "_version",
        "appname",
    )

    def __init__(
        self,
        appname,
        version=None,
        no_period=True,
        no_space=True,
        no_underscore=True,
    ):
        """Constructor"""
        super().__init__()

        if is_not_ok(appname):  # pragma: no branch
            msg_warn = (
                f"appname is required got {appname!r}. package name is "
                "needed to query package for author name"
            )
            raise ValueError(msg_warn)

        self._appauthor = None
        self.appname = appname
        self.no_period = no_period
        self.no_space = no_space
        self.no_underscore = no_underscore

        # Set a default
        self._version = None
        # Property setter only accepts supported type
        self._version = version

    @property
    def version(self):
        """property getter

        :rtype: str | None
        """
        ret = self._version
        return ret

    @version.setter
    def version(self, val):
        """property setter. Does not confirm version is a semantic version str.

        :type val: typing.Any
        """
        if is_ok(val):  # pragma: no branch
            self._version = val

    @property
    def no_period(self):
        """Author name period should be normalized.

        :rtype: bool
        """
        ret = self._no_period
        return ret

    @no_period.setter
    def no_period(self, val):
        """no_period setter

        :type val: typing.Any
        """
        if val is None or not isinstance(val, bool):
            self._no_period = True
        else:
            self._no_period = val

    @property
    def no_space(self):
        """Whitespace within author name should be normalized.

        :rtype: bool
        """
        ret = self._no_space
        return ret

    @no_space.setter
    def no_space(self, val):
        """no_space setter

        :type val: typing.Any
        """
        if val is None or not isinstance(val, bool):
            self._no_space = True
        else:
            self._no_space = val

    @property
    def no_underscore(self):
        """If True, underscore in author name is normalized.

        :rtype: bool
        """
        ret = self._no_underscore
        return ret

    @no_underscore.setter
    def no_underscore(self, val):
        """no_space setter

        :type val: typing.Any
        """
        if val is None or not isinstance(val, bool):
            self._no_underscore = True
        else:
            self._no_underscore = val

    @property
    def appauthor(self):
        """Ideally a package author would provide their name. Unfortunity
        there are exceptions, e.g. ``selenium``.

        :rtype: str | None
        """
        ret = self._appauthor
        return ret

    @appauthor.setter
    def appauthor(self, val):
        """Very important setter. Apply author name normalization.

        On MacOS, the app author name is needed to avoid possible app
        naming collisions with other apps. To satisfy MacOS, ``appauthor``
        differentiates between these same named apps.

        If a package doesn't reveal the author, the appauthor is None.
        The (relative) folder path becomes ``[appname]/None``. So coder should
        use the class property setter, appauthor, to specify what they'd like
        the appauthor to be.

        :param val:

           Override appauthor especially relevent when package rudely
           lacks attribution.

        :type val: typing.Any
        """
        if val is not None and isinstance(val, str):  # pragma: no branch
            self._appauthor = _author_normalize(
                val,
                self.no_period,
                self.no_space,
                self.no_underscore,
            )


class DestFolderSite(XDGBase):
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

    __slots__ = ("_multipath",)

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
        super().__init__(
            appname,
            version=version,
            no_period=author_no_period,
            no_space=author_no_space,
            no_underscore=author_no_underscore,
        )
        # bypass property setter. ``_get_author`` also,
        # from package, retrieves author name
        self._appauthor = _get_author(
            self.appname,
            no_period=self.no_period,
            no_space=self.no_space,
            no_underscore=self.no_underscore,
        )
        self._multipath = multipath

    @property
    def multipath(self):
        """multipath getter

        :rtype: bool
        """
        ret = self._multipath
        return ret

    @multipath.setter
    def multipath(self, val):
        """multipath setter

        :type val: typing.Any
        """
        # None --> False
        self._multipath = bool(val)

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


class DestFolderUser(XDGBase):
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

    __slots__ = ("_opinion", "_roaming")

    def __init__(
        self,
        appname,
        author_no_period=True,
        author_no_space=True,
        author_no_underscore=True,
        version=None,
        roaming=False,
        opinion=True,
    ):
        """Class constructor"""
        super().__init__(
            appname,
            version=version,
            no_period=author_no_period,
            no_space=author_no_space,
            no_underscore=author_no_underscore,
        )
        # bypass property setter. ``_get_author`` also,
        # from package, retrieves author name
        self._appauthor = _get_author(
            self.appname,
            no_period=self.no_period,
            no_space=self.no_space,
            no_underscore=self.no_underscore,
        )
        # default is False
        self._roaming = roaming
        # default is True
        self._opinion = opinion if opinion is not None else True

    @property
    def opinion(self):
        """Property getter

        :rtype: bool
        """
        ret = self._opinion
        return ret

    @opinion.setter
    def opinion(self, val):
        """Property getter

        :type val: typing.Any
        """
        self._opinion = bool(val)

    @property
    def roaming(self):
        """Property getter

        :rtype: bool
        """
        ret = self._roaming
        return ret

    @roaming.setter
    def roaming(self, val):
        """Property getter

        :type val: typing.Any
        """
        self._roaming = bool(val)

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
