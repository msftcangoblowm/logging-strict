"""
.. module:: docs.conf
   :platform: Unix
   :synopsis: Sphinx dynamic configuration

.. moduleauthor:: Dave Faulkmore <faulkmore telegram>

..

Sphinx dynamic configuration
"""

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
version = "1.2.27"
# The full version, including alpha/beta/rc tags.
release = "1.2.27"
# The date of release, in "monthname day, year" format.
release_date = "April 5, 2024"
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
htmlhelp_basename = f"{slug}doc"
# .. |doc-url| replace:: https://logging_strict.readthedocs.io/en/{release}
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
        "manual",
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
# Dict -- Static
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

# Creating ``objects.inv`` files for third party packages that lack them
# https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html
# `sphobjinv pypi <https://pypi.org/project/sphobjinv/>`_
# `sphobjinv docs <https://sphobjinv.readthedocs.io/en/v2.3.1/customfile.html>`_
# https://sphobjinv.readthedocs.io/en/v2.3.1/api_usage.html#exporting-an-inventory
intersphinx_mapping = {
    "python": (
        "https://docs.python.org/3",
        ("objects-python.inv", None),
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
        "https://github.com/psf",
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

# https://www.sphinx-doc.org/en/master/usage/extensions/extlinks.html
# extlinks_detect_hardcoded_links = True


def strip_anchor(widget_name: str) -> str:
    if "#" in widget_name:
        parts = widget_name.split("#")
        ret = parts[0]
    else:
        ret = widget_name
    return ret


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


# https://docs.python.org/3/library/importlib.metadata.html
# https://docs.python.org/3/library/importlib.html#module-importlib.resources
# list(dist.metadata)
# ['Metadata-Version', 'Name', 'Version', 'Summary', 'Home-page',
#     'Author', 'Author-email', 'License', 'Keywords', 'Platform',
#     'Classifier', 'Classifier', 'Classifier', 'Classifier',
#    'Classifier', 'Classifier', 'Classifier', 'Classifier',
#    'Classifier', 'Classifier', 'Classifier', 'Requires-Python',
#    'Description-Content-Type', 'Requires-Dist', 'Requires-Dist',
#    'Requires-Dist', 'Requires-Dist']
#


# -- Project information -----------------------------------------------------
# project = dist.metadata.get("Name")
# author = dist.metadata.get("Author")
# copyright = f"Copyright 2023 {author}"

#    The short X.Y version
# version = version_short
#    The full version, including alpha/beta/rc tags
# release = __release__
# description = dist.metadata.get("Summary")

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.

# extensions = []
# extensions.append('sphinx.ext.autodoc')
# extensions.append('sphinxcontrib.fulltoc')
# extensions.append('sphinx.ext.todo')
# extensions.append('sphinx.ext.autosectionlabel')
# Ideally would like async fcns and async methods to be marked as
#     `async`. This is not ideal, but preferrable to not being marked at
#     all.
#
# extensions.append('sphinxcontrib.asyncio')
# extensions.append('sphinx.ext.githubpages')
# extensions.append('sphinx_paramlinks')


# When modules break the code documentation build process
# autodoc_mock_imports = ["systray_udisks2.util_logging2"]
# autodoc_mock_imports = []

# Add any paths that contain templates here, relative to this directory.

# templates_path = ['_templates']


# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']

# source_suffix = '.rst'


# The master toctree document.

# master_doc = 'index'


# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.

# language = 'en'


# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path .

# exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# The name of the Pygments (syntax highlighting) style to use.

# pygments_style = 'sphinx'


# :numref:`target to image` --> Fig. N
# https://docs.readthedocs.io/en/stable/guides/cross-referencing-with-sphinx.html#the-numref-role
# numfig = True

# Make sure the target is unique
# https://docs.readthedocs.io/en/stable/guides/cross-referencing-with-sphinx.html#automatically-label-sections
# autosectionlabel_prefix_document = True

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
# https://alabaster.readthedocs.io/en/latest/customization.html
# https://github.com/bitprophet/alabaster/blob/master/alabaster/theme.conf
# html_theme = 'alabaster'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#

# html_theme_options = {}
# html_theme_options["show_relbars"] = True
# html_theme_options["description"] = proj_description
# Place in ``_static``
# html_theme_options["logo"] = "detective-woman-folder-with-cat-bookmark.svg"
# If logo contains project name, turn off, above side bar, display of
# project name
# html_theme_options["logo_name"] = False


# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".

# html_static_path = ['_static']


# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# The default sidebars (for documents that don't match any pattern) are
# defined by theme itself.  Builtin themes are using these templates by
# default: ``['localtoc.html', 'relations.html', 'sourcelink.html',
# 'searchbox.html']``.
#


# html_sidebars = {
#     '**': [
#         'about.html',
#         'searchbox.html',
#         'navigation.html',
#         'relations.html',
#     ],
# }


# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.

# htmlhelp_basename = f'{proj_project}doc'


# -- Options for LaTeX output ------------------------------------------------


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


# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).

# latex_documents = [
#     (proj_master_doc, f'{slug}.tex', f'{proj_project} Documentation', proj_authors, 'manual'),
# ]


# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).

# man_pages = [(proj_master_doc, slug, f'{proj_project} Documentation', [proj_authors], 1)]


# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)

# texinfo_documents = [
#     (proj_master_doc, slug, f'{proj_project} Documentation', proj_authors, slug,
#      proj_description, 'Miscellaneous'),
# ]

# -- Extension configuration -------------------------------------------------
pass
