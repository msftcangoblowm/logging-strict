import re
import sys
from pathlib import Path

from packaging.version import parse
from sphinx_pyproject import SphinxConfig

from logging_strict.constants import __version__ as proj_version
from logging_strict.util.pep518_read import find_project_root

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
path_docs = Path(__file__).parent
path_package_base = path_docs.parent

sys.path.insert(0, str(path_package_base))  # Needed ??

# pyproject.toml search algo. Credit/Source: https://pypi.org/project/black/
srcs = (path_package_base,)
t_root = find_project_root(srcs)

config = SphinxConfig(
    t_root[0] / "pyproject.toml",
    globalns=globals(),
    config_overrides={"version": proj_version},  # dynamic version setuptools_scm
)

# :pep:`621` attributes
# https://sphinx-pyproject.readthedocs.io/en/latest/
# api.html#sphinx_pyproject.SphinxConfig.name"""
proj_project = config.name
proj_description = config.description
proj_authors = config.author

# X.Y.Z version. Including alpha/beta/rc tags.
# https://sphinx-pyproject.readthedocs.io/en/latest/
# api.html#sphinx_pyproject.SphinxConfig.version
# https://peps.python.org/pep-0621/#version
# https://packaging.python.org/en/latest/specifications/core-metadata/#version

slug = re.sub(r"\W+", "-", proj_project.lower())
proj_master_doc = config.get("master_doc")


# Version is dynamic. Dependent on git and this file is edited by ``igor.py``

# @@@ editable
copyright = "2023–2024, Dave Faulkmore"
# The short X.Y.Z version.
version = "1.4.2"
# The full version, including alpha/beta/rc tags.
release = "1.4.2"
# The date of release, in "monthname day, year" format.
release_date = "December 30, 2024"
# @@@ end

# release = config.version
v = parse(release)
version_short = f"{v.major}.{v.minor}"
# version_xyz = f"{v.major}.{v.minor}.{v.micro}"
version_xyz = version
project = f"{proj_project} {version}"

###############
# Dynamic
###############
rst_epilog = """
.. |project_name| replace:: {slug}
.. |package-equals-release| replace:: logging_strict=={release}
""".format(
    release=release, slug=slug
)

# https://alabaster.readthedocs.io/en/latest/customization.html
# https://pypi.org/project/sphinx_external_toc/
html_theme_options = {
    "description": proj_description,
    "show_relbars": True,
    "logo_name": False,
    "logo": "logging-strict-logo.svg",
    "show_powered_by": False,
}

latex_documents = [
    (
        proj_master_doc,
        f"{slug}.tex",
        f"{proj_project} Documentation",
        proj_authors,
        "manual",  # manual, howto, jreport (Japanese)
        True,
    )
]
man_pages = [
    (
        proj_master_doc,
        slug,
        f"{proj_project} Documentation",
        [proj_authors],
        1,
    )
]
texinfo_documents = [
    (
        proj_master_doc,
        slug,
        f"{proj_project} Documentation",
        proj_authors,
        slug,
        proj_description,
        "Miscellaneous",
    )
]

#################
# Static
#################
ADDITIONAL_PREAMBLE = r"""
\DeclareUnicodeCharacter{20BF}{\'k}
"""

latex_elements = {
    "sphinxsetup": "verbatimforcewraps",
    "extraclassoptions": "openany,oneside",
    "preamble": ADDITIONAL_PREAMBLE,
}

html_sidebars = {
    "**": [
        "about.html",
        "searchbox.html",
        "navigation.html",
        "relations.html",
    ],
}

intersphinx_mapping = {
    "python": (  # source https://docs.python.org/3/objects.inv
        "https://docs.python.org/3",
        ("objects-python.inv", "objects-python.txt"),
    ),
    "setuptools-scm": (
        "https://setuptools-scm.readthedocs.io/en/latest",
        ("objects-setuptools-scm.inv", "objects-setuptools-scm.txt"),
    ),
    "logging-strict": (
        "https://logging-strict.readthedocs.io/en/latest",
        ("objects-logging-strict.inv", "objects-logging-strict.txt"),
    ),
    "strictyaml-docs": (
        "https://hitchdev.com/strictyaml",
        ("objects-strictyaml-docs.inv", "objects-strictyaml-docs.txt"),
    ),
    "strictyaml-source": (
        "https://github.com/crdoconnor/strictyaml",
        ("objects-strictyaml-source.inv", "objects-strictyaml-source.txt"),
    ),
    "textual-docs": (
        "https://textual.textualize.io",
        ("objects-textual-docs.inv", "objects-textual-docs.txt"),
    ),
    "black": (
        "https://github.com/psf/black",
        ("objects-black.inv", "objects-black.txt"),
    ),
    "coverage-docs": (
        "https://coverage.readthedocs.io/en/latest",
        ("objects-coverage-docs.inv", "objects-coverage-docs.txt"),
    ),
    "coverage-source": (
        "https://github.com/nedbat/coveragepy",
        ("objects-coverage-source.inv", "objects-coverage-source.txt"),
    ),
}
intersphinx_disabled_reftypes = ["std:doc"]

extlinks = {
    "pypi_org": (  # url to: aiologger
        "https://pypi.org/project/%s",
        "%s",
    ),
}

# spoof user agent to prevent broken links
# curl -A "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:24.0) Gecko/20100101 Firefox/24.0" --head "https://github.com/python/cpython/blob/3.12/Lib/unittest/case.py#L193"
linkcheck_request_headers = {
    "https://github.com/": {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:24.0) Gecko/20100101 Firefox/24.0",
    },
    "https://docs.github.com/": {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:24.0) Gecko/20100101 Firefox/24.0",
    },
}

# latex_elements = {
#     # The paper size ('letterpaper' or 'a4paper').
#     #
#     # 'papersize': 'letterpaper',
#
#     # The font size ('10pt', '11pt' or '12pt').
#     #
#     # 'pointsize': '10pt',
#
#     # Additional stuff for the LaTeX preamble.
#     #
#     # 'preamble': '',
#
#     # Latex figure (float) alignment
#     #
#     # 'figure_align': 'htbp',
#     'sphinxsetup': 'verbatimforcewraps', # https://github.com/sphinx-doc/sphinx/issues/5974#issuecomment-776283378
#     'extraclassoptions': 'openany,oneside',
# }

# When modules break the code documentation build process
# autodoc_mock_imports = ["systray_udisks2.util_logging2"]
# autodoc_mock_imports = []

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']

# source_suffix = '.rst'

# :numref:`target to image` --> Fig. N
# https://docs.readthedocs.io/en/stable/guides/cross-referencing-with-sphinx.html#the-numref-role
# numfig = True

# Make sure the target is unique
# https://docs.readthedocs.io/en/stable/guides/cross-referencing-with-sphinx.html#automatically-label-sections
# autosectionlabel_prefix_document = True

# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).

# man_pages = [(proj_master_doc, slug, f'{proj_project} Documentation', [proj_authors], 1)]
pass
