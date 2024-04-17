"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

git --> setuptools-scm --> kitting (howto.txt / igor.py / Makefile) --> semantic versioning

.. py:data:: _map_release
   :type: types.MappingProxyType
   :value: types.MappingProxyType({"alpha": "a", "beta": "b", "candidate": "rc"})

   Mapping of release levels. So can gracefully go back and forth

Release phases
---------------

Without SETUPTOOLS_SCM_PRETEND_VERSION_FOR_SPHINX_EXTERNAL_TOC_STRICT environmental variable
locals are included in version

e.g. "0.1.1.dev0+g4b33a80.d20240129" local is "g4b33a80.d20240129"

When releasing this is not what is wanted, so use
SETUPTOOLS_SCM_PRETEND_VERSION_FOR_SPHINX_EXTERNAL_TOC_STRICT with the version

- Current version

  .. code-block:: shell

     PYTHONWARNINGS="ignore" python setup.py --version


- Release by tag aka final

  .. code-block:: shell

     PYTHONWARNINGS="ignore" SETUPTOOLS_SCM_PRETEND_VERSION_FOR_SPHINX_EXTERNAL_TOC_STRICT="$(git describe --tag)" python setup.py --version
     SETUPTOOLS_SCM_PRETEND_VERSION_FOR_SPHINX_EXTERNAL_TOC_STRICT="$(git describe --tag)" python -m build


- alpha: a, beta: b, or candidate: rc

  .. code-block:: shell

     PYTHONWARNINGS="ignore" SETUPTOOLS_SCM_PRETEND_VERSION_FOR_SPHINX_EXTERNAL_TOC_STRICT="0.1.1a1" python setup.py --version
     SETUPTOOLS_SCM_PRETEND_VERSION_FOR_SPHINX_EXTERNAL_TOC_STRICT="0.1.1a1" python -m build


- dev

  .. code-block:: shell

     PYTHONWARNINGS="ignore" SETUPTOOLS_SCM_PRETEND_VERSION_FOR_SPHINX_EXTERNAL_TOC_STRICT="0.1.1a1.dev1" python setup.py --version
     SETUPTOOLS_SCM_PRETEND_VERSION_FOR_SPHINX_EXTERNAL_TOC_STRICT="0.1.1a1.dev1" python -m build


Move the tag past post commits

- post

  .. code-block:: shell

     PYTHONWARNINGS="ignore" SETUPTOOLS_SCM_PRETEND_VERSION_FOR_SPHINX_EXTERNAL_TOC_STRICT="0.1.1.post1" python setup.py --version
     SETUPTOOLS_SCM_PRETEND_VERSION_FOR_SPHINX_EXTERNAL_TOC_STRICT="0.1.1.post1" python -m build


.. py:data:: __all__
   :type: tuple[str, str, str]
   :value: ("sanitize_tag", "get_version", "readthedocs_url")

   Module exports

"""

import types

try:
    from packaging.version import InvalidVersion
    from packaging.version import Version as Version
except ImportError:  # pragma: no cover
    from setuptools.extern.packaging.version import InvalidVersion  # type: ignore
    from setuptools.extern.packaging.version import Version as Version  # type: ignore

__all__ = (
    "sanitize_tag",
    "get_version",
    "readthedocs_url",
)

_map_release = types.MappingProxyType({"alpha": "a", "beta": "b", "candidate": "rc"})


def _strip_epoch(ver):
    """Strip epoch

    :param ver: May contain epoch, ``v``, and local
    :type ver: str
    :returns: epoch and remaining str including ``v`` and local
    :rtype: collections.abc.Sequence[str | None, str]
    :meta private:
    """
    try:
        idx = ver.index("!")
    except ValueError:
        # Contains no epoch
        epoch = None
        remaining = ver
    else:
        epoch = ver[: idx + 1]
        remaining = ver[idx + 1 :]

    return epoch, remaining


def _strip_local(ver):
    """Strip local from end of version string

    From ``0!v1.0.1.a1dev1+g4b33a80.d20240129``

    local: ``g4b33a80.d20240129``

    remaining: ``0!v1.0.1.a1dev1``

    :returns: local and remaining
    :rtype: collections.abc.Sequence[str | None, str]
    :meta private:
    """
    try:
        idx = ver.index("+")
    except ValueError:
        # Contains no local
        local = None
        remaining = ver
    else:
        local = ver[idx + 1 :]
        remaining = ver[:idx]

    return local, remaining


def remove_v(ver):
    """Remove prepended v. e.g. From ``0!v1.0.1.a1dev1+g4b33a80.d20240129``

    Will not work on an initial untagged version, ``0.1.dev0.d20240213``

    :param ver: Non-initial untagged version
    :type ver: str
    :returns: original str without the v. Includes epoch and local
    :rtype: str
    """
    epoch, remaining = _strip_epoch(ver)
    local, remaining = _strip_local(remaining)

    # If prepended "v", remove it. epoch e.g. ``1!v1.0.1`` would conceal the "v"
    if remaining.startswith("v"):
        remaining = remaining[1:]

    ret = epoch if epoch is not None else ""
    ret += remaining

    if local is not None:
        ret += f"+{local}"
    else:  # pragma: no cover
        pass

    return ret


def sanitize_tag(ver):
    """Avoid reinventing the wheel, leverage Version

    ``final`` is not valid

    :param ver: raw semantic version
    :type ver: str
    :returns: Sanitized semantic version str
    :rtype: str
    :raises:

       - :py:exc:`ValueError` -- Invalid token within Version str

    """
    # Careful! Will choke on initial untagged version, e.g. ``0.1.dev0.d20240213``
    str_remaining_whole = remove_v(ver)

    # Strip epoch, if exists
    epoch, str_remaining_stripped = _strip_epoch(str_remaining_whole)

    """Strip local, if exists

    Will fail to detect an initial untagged version e.g. '0.1.dev0.d20240213'"""
    local, str_remaining_stripped = _strip_local(str_remaining_stripped)

    # Problematic
    # '0.1.dev0.d20240213'. Untagged version. Try remove from last period
    # 0.1.1.candidate1dev1+g4b33a80.d20240129
    try:
        v = Version(str_remaining_whole)
    except InvalidVersion:
        is_problem = True
    else:
        is_problem = False

    if is_problem:
        lst = str_remaining_whole.split(".")

        ver_try = ".".join(lst[:-1])
        try:
            v = Version(ver_try)
        except InvalidVersion:
            is_still_issue = True
        else:  # pragma: no cover Do nothing
            is_still_issue = False
    else:  # pragma: no cover Do nothing
        is_still_issue = False

    if is_still_issue:
        try:
            v = Version(str_remaining_whole)
        except InvalidVersion as e:
            msg = f"Version contains invalid token. {e}"
            raise ValueError(msg) from e
    else:  # pragma: no cover Do nothing
        pass

    ret = str(v)

    # Strip epoch and local, if exists
    epoch, ret = _strip_epoch(ret)
    local, ret = _strip_local(ret)

    return ret


def readthedocs_url(package_name, ver_="latest"):
    """Avoid reinventing the wheel

    :param package_name:

       Differences from app name, contains hyphens rather than underscores

    :param ver_: Default "latest". Semantic version string
    :type ver_: str
    :returns:

       url to readthedocs.io for a semantic version of the docs, not necessarily the latest

    :rtype: str
    """
    # app-name --> package_name
    if "_" in package_name:
        package_name = package_name.replace("_", "-")
    else:  # pragma: no cover
        pass

    if ver_ is None or (ver_ is not None and not isinstance(ver_, str)):
        ver_ = "latest"
    else:  # pragma: no cover
        pass

    if ver_ != "latest":
        ver = sanitize_tag(ver_)
    else:  # pragma: no cover
        ver = ver_

    ret = f"https://{package_name}.readthedocs.io/en/{ver}"

    return ret


def get_version(ver, is_use_final=False):
    """Semantic version string broken into parts

    :param ver: A semantic version string
    :type ver: str
    :param is_use_final:

       Default False. ``final`` is not normally valid within a semantic
       version string. The use of final may be used to indicate intention of creating
       a tagged release version. If all the stars are aligned and its
       G'ds Will. If not, ``post release`` version(s) would occur and
       ``final`` would be incorrect.

       Don't create invalid semantic version strings cuz its convenient.
       Don't use this feature!

    :type is_use_final: bool
    :returns:

       Semantic version broken into parts: major, minor, micro,
       release level, serial. And _dev

    :rtype: tuple[tuple[int, int, int, str, int], int]
    """
    if is_use_final is None or not isinstance(is_use_final, bool):
        is_use_final = False
    else:  # pragma: no cover
        pass

    # epoch and locals ignored
    _v = Version(ver)
    _dev = _v.dev if _v.is_devrelease else 0

    if not _v.is_prerelease and not _v.is_postrelease:
        # ``final`` means intend to bump version. Not actually valid
        releaselevel = "" if not is_use_final else "final"
        serial = 0
        _dev = 0
    elif _v.is_prerelease and not _v.is_postrelease:
        # Requires long
        if _v.is_devrelease and _v.pre is None:
            # dev
            serial = 0
            releaselevel = ""  # alpha??
        else:
            # alpha beta, candidate, a, b, or rc
            t_pre = _v.pre
            short = t_pre[0]
            serial = t_pre[1]
            for long_, short_ in _map_release.items():
                if short_ == short:
                    releaselevel = long_
                else:  # pragma: no cover continue
                    pass
    elif not _v.is_prerelease and _v.is_postrelease:
        releaselevel = "post"
        serial = _v.post
    elif _v.is_prerelease and _v.is_postrelease:  # pragma: no cover
        # impossible
        pass
    else:  # pragma: no cover
        pass

    return (_v.major, _v.minor, _v.micro, releaselevel, serial), _dev
