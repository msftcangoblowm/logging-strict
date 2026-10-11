"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

.. py:data:: __all__
   :type: tuple[str]
   :value: ("MyLogger",)

"""

from .logging_yaml_abc import (
    VERSION_FALLBACK,
    YAML_LOGGING_CONFIG_SUFFIX,
    LoggingYamlType,
)

__all__ = ("MyLogger",)

#: str: Hardcoded package name. Doing this is obsolete, but in context of testing is ok.
g_package_second_party = "asz"


def file_stem(
    genre="mp",
    version=VERSION_FALLBACK,
    flavor=g_package_second_party,
):
    """Test implementation of file_stem.

    :type genre: str | None
    :type version: str | None
    :type flavor: str | None
    :rtype: str
    """
    return f"{genre}_{version}_{flavor}"


def file_name(
    category="worker",
    genre="mp",
    version=VERSION_FALLBACK,
    flavor=g_package_second_party,
):
    """Test implementation of file_name.

    :type category: str | None
    :type genre: str | None
    :type version: str | None
    :type flavor: str | None
    :rtype: str
    """
    stem = file_stem(genre=genre, version=version, flavor=flavor)

    ret = f"{stem}.{category}{YAML_LOGGING_CONFIG_SUFFIX}"
    return ret


class MyLogger(LoggingYamlType):
    """A basic implementation

    :vartype package_name: str
    :vartype func: collections.abc.Callable[[str], pathlib.Path]
    """

    #: typing.ClassVar[str]: Nonsense logging YAML config file suffixes
    suffixes = ".my_logger"

    def __init__(self, package_name, func):
        """Mock class constructor"""
        super().__init__()
        self._package = package_name
        self.func = func

    @property
    def file_stem(self):
        """Test implementation of property file_stem.

        :rtype: str
        """
        ret = file_stem()
        return ret

    @property
    def file_name(self):
        """Test implementation of property file_name.

        :rtype: str
        """
        ret = file_name()
        return ret

    @property
    def package(self):
        """Test implementation of property package. Subfolder relative
        path to where package resources are extracted.

        :rtype: str
        """
        return self._package

    @property
    def dest_folder(self):  # pragma: no cover
        """Package resource destination folder Path
        :rtype: pathlib.Path
        """
        ret = self.func(self.package)
        return ret

    @property
    def version(self):  # pragma: no cover
        """Required by ABC

        :rtype: str | None
        """
        return None

    @property
    def genre(self):  # pragma: no cover
        """Required by ABC

        :rtype: str | None
        """
        return None

    @property
    def flavor(self):  # pragma: no cover
        """Required by ABC

        :rtype: str | None
        """
        return None

    @property
    def category(self):  # pragma: no cover
        """Required by ABC

        :rtype: str | None
        """
        return None

    def extract(self, path_relative_package_dir=""):  # pragma: no cover
        """Nonsense package resource extract implementation.

        :type path_relative_package_dir: pathlib.Path | str | None
        :rtype: str
        """
        ret = f"relativepath/{self.file_name}"
        return ret
