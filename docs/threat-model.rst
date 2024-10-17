Threat model
=============

Why?
-----

Any project, which has any YAML or binary files, needs to identify
threats.

Conducted by this author, **not by a third party** (security audit).

Threats target the sewer pipes, so lets identify where to target

Contact
--------

`mastodon <https://mastodon.social/@msftcangoblowme>`_

Can't contact author?:

- disregard this document

- perform your own security audit

- fork this project

Contact author topics:

- vulnerability found

- request to clarify

- identify other threats

- donation (force the author to act or dependency in your projects)

- paid consulting request

Containerization
-----------------

These are the resources this package accesses

Folders
^^^^^^^^

- xdg user data folder

- :code:`$HOME/.local/share/logging_strict`

- /tmp sub-folders created and removed by unittest package, tempfile

Network
^^^^^^^^

Package **does not** access web resources

Sewer pipes
------------

Unreproducible binary blobs
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Binary files:

- in docs/_static folder

  Sewer pipe: No
  Affects: None
  Mitigation strategy: None needed
  Descrption:

  docs/_static/validate_flavor_asz.tape --> docs/_static/validate_flavor_asz.gif

  Shown in README.rst

  For svg files, should also be png files, but oddly aren't. So no logo docs
  when exported as pdf

- docs/*.txt --> docs/*.inv

  Sewer pipe: Yes
  Affects: backdoor can load new code in the form of tests. Attack surface
  infinite so must mitigate.
  Mitigation strategy: Most distros, have downgraded to xz-5.4.6
  On affected machines, open the package manager and run an update. Then
  check with :command:`xz --version`
  Descrption: .inv files contains a clear text header and zlib compressed content.

  Python zlib uses liblzma-devel, part of xz package.

  Compromised versions: xz-5.6.0 and xz-5.6.1

.. seealso::

  CVE-2024-3094 (broken link)
  https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2024-3094

   Discovered: 2024/03/29

   `Discovery reveal email <https://www.openwall.com/lists/oss-security/2024/03/29/4>`_

Makefile
^^^^^^^^^

- Files: Makefile and docs/Makefile

Sewer pipe: Yes
Affects: devs or those building from source code
Mitigation strategy: Any PRs **must** be reviewed
Descrption: Makefile(s) contain bash

The release tarball and whl are available from github and are created
by github CI/CD, not the author

Dependencies
^^^^^^^^^^^^^

- strictyaml

  Sewer pipe: No
  Affects: Everyone
  Mitigation strategy: fork project
  Description: Lacks automated testing, coverage, and strict type checking

  This package and author('s goals) are abnormal (not evil). Trying to innovate
  the wheel (hitch) is noble, but this falls short. This project must prove it's
  assertions. The docs are stunningly beautiful.

  Unmaintainable and fragile

- sphinx_external_toc

  Sewer pipe: Yes
  Affects: building docs. Specifically, table of contents
  Mitigation strategy: fork project
  Description: This sphinx plugin uses dependency pyyaml. pyyaml is not safe. Does
  not pass thru a schema to validate the yaml file

unittest suite
"""""""""""""""

Sewer pipe: Yes
Affects: Everyone
Mitigation strategy: Any PRs **must** be reviewed
Description: Writes to tmp folder. Self generates some simple unittests

Priority (in order)
--------------------

- sphinx_external_toc

- strictyaml

Not planned
------------

- self generated unittests

- write to /tmp folders (not a threat)

- Makefile(s). No known Python alternatives. Bash is a threat!

pyyaml still?
--------------

pyyaml is a dependency of:

- sphinx-external-toc-strict --> myst-parser --> pyyaml

  sphinx --> myst-parser --> pyyaml

- pytest-regressions --> pyyaml

- pre-commit --> pyyaml

How to reproduce
^^^^^^^^^^^^^^^^^

grep these folders for pyyaml:

- docs/
- requirements/
