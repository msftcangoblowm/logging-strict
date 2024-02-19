from __future__ import annotations

from setuptools import setup
from setuptools_scm import ScmVersion
from setuptools_scm.version import get_local_dirty_tag


def _clean_version() -> dict[str, str]:
    """scm is generating developer versions, rather than tagged versions

    dict communicating between :menuselection:`setuptools_scm --> setuptools`

    :returns: start folder relative path. e.g. tests/ui
    :rtype: dict[str, str]

    .. seealso::

       `Credit <https://stackoverflow.com/q/73157896>`_

    """

    def get_version(version: ScmVersion) -> str:
        """Get local scheme. Aka tagged version

        :param version: Version as setuptools_scm grabs from vcs
        :type version: :py:class:`setuptools_scm.ScmVersion`
        :returns: local scheme
        :rtype: str
        """
        # str(version.tag)
        return version.format_with("{tag}")

    def clean_scheme(version: ScmVersion) -> str:
        """Full version from vcs

        :param version: Version as setuptools_scm grabs from vcs
        :type version: :py:class:`setuptools_scm.ScmVersion`
        :returns: version scheme
        :rtype: str
        """
        return get_local_dirty_tag(version) if version.dirty else "+clean"

    return {"local_scheme": get_version, "version_scheme": clean_scheme}


setup(
    use_scm_version=_clean_version,
)
