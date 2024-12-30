.. this will be appended to README.rst

Changelog
=========

..

   Feature request
   .................

   - Framework classifier to advertise package contains unverified
     logging config YAML files

   - Within a package, centralized config file. With known file name and file format.
     Lists logging config YAML files.
     Would remove the need to specify relative path to package resource

   - tox-gh-matrix produces the version matrix from tox config file
     this is then feed into gh matrix.

     https://pypi.org/project/tox-gh-matrix/

   - remove get-pypi-latest-version
     code to get the version w/o dependencies
     https://gist.github.com/RhetTbull/478a1a2b90fcfa3a4cd3e14963799879

   - Run coverage, upload results, and display badge

     https://github.com/pytest-dev/pytest/blob/main/.github/workflows/test.yml

   - Close stale issues after 14 days

   https://github.com/pytest-dev/pytest/blob/main/.github/workflows/stale.yml

   - Gracefully handle sigpipe error around validate entrypoint

     https://github.com/pytest-dev/pytest/blob/main/src/_pytest/config/__init__.py#L190

   Known regressions
   ..................

   - LoggingConfigYaml.extract if package name is not a valid dotted path
     e.g. logging-strict bombs and is hard to spot. Create an Issue then a commit

   - strictyaml.scalar.Time does not exist. So field asTime can't be supported
   - strictyaml has no automated tests
   - strictyaml has no typing hint stubs. ignore_missing_imports

   - ci/kit.yml in sdist Set output tag will be branch name, not tag name see ci/release.yml

   Commit items for NEXT VERSION
   ..............................

.. scriv-start-here

.. _changes_1-4-2:

Version 1.4.2 — 2024-12-30
--------------------------

- fix: package name to valid dotted path before package resource extraction (#3)
- chore(pre-commit): add mypy check

.. _changes_1-4-1:

Version 1.4.1 — 2024-12-29
--------------------------

- fix(logging_api): extract from non-installed package raise ImportError (#2)
- fix(logging_api): in fcn worker_yaml_curated remove ImportError check
- ci: bump gha action versions
- ci: add templates for PR feature request and bug report

.. _changes_1-4-0:

Version 1.4.0 — 2024-12-18
--------------------------

- fix: yaml logger package_name placeholder replace with target package name
- ci(testsuite): fix lack hyphen between pypi and version
- chore: configure interrogate in pyproject.toml and pre-commit config
- docs: fill in missing in-code documentation

.. _changes_1-3-6:

Version 1.3.6 — 2024-10-19
--------------------------

- chore: bump cffi to 1.17.1 add py313 and musllinux aarch64 support (#1)
- test: fix windows and macos specific errors
- ci(tox-test.ini): give tox-gh-actions a try
- ci(tox.ini): use testenv basepython to set each env python version
- ci(tox-test.ini): add seperate tests tox config file
- fix(logging_yaml_validate): MapValidator --> MapPattern
- feat(util_root): add detect elevated privledge on Windows
- fix: remove unmaintained dependency get-pypi-latest-version
- fix(util_root): no os.getuid on windows
- ci(testsuite): turn on test platforms windows and macos

.. _changes_1-3-5:

Version 1.3.5 — 2024-10-17
--------------------------

- docs: fix links and doctest issues
- test(util_root): on Windows, getpwnam become module level variable allow patch
- fix(logging_yaml_validate): fix import to strictyaml.validators.MapValidator
- fix(util_root): no pwd module on Windows. shutil.chown also not Windows

.. _changes_1-3-4:

Version 1.3.4 — 2024-10-16
--------------------------

- docs(readthedocs): bump py39 --> py310

.. _changes_1-3-3:

Version 1.3.3 — 2024-10-16
--------------------------

- refactor(context_locals): T and P to private module variables _T and _P
- docs: clean up toc remove headers module objects and module private variables
- docs: author contact mastodon not telegram

.. _changes_1-3-2:

Version 1.3.2 — 2024-10-15
--------------------------

- ci: bump sigstore/gh-action-sigstore-python to v3.0.0

.. _changes_1-3-1:

Version 1.3.1 — 2024-10-15
--------------------------

- fix: unlock production dependencies
- fix(pins.pip): unlock python-dateutil constraint
- chore: update/bump requirements to latest
- chore(tox.ini): sphinx is py310+ docs py39 --> py310
- ci(test-coverage): pip requirements on same line

.. _changes_1-3-0:

Version 1.3.0 — 2024-04-19
---------------------------

- ci: actions/setup-python remove option cache pip
- docs: add todo page
- ci(pre-commit): remove remove-intersphinx-inventory-files rtd needs docs/*.inv
- ci(tox): in docs, remove calls to build_inv and clean_inv
- docs(Makefile): build_inv and clean_inv use relative path
- docs: add links to pypi github sissues changelog chat
- docs: remove objects-python.txt too heavy. rtd needs docs/*.inv
- docs: enable sphinx extensions sphinx-external-toc-strict and myst-parser
- docs: requirement sphinx-external-toc --> sphinx-external-toc-strict
- fix: python-dateutil version pinned. Resolve dependency conflict

.. _changes_1-2-32:

Version 1.2.32 — 2024-04-17
---------------------------

- docs: generate intersphinx .inv files so only commit plain text files
- docs(Makefile): add targets build_inv inv2txt clean_inv
- docs: remove license.rst and sphinx-licenseinfo extension
- ci(tox): docs call make build_inv afterwards call make clean_inv
- ci(pre-commit): add remove-intersphinx-inventory-files
- ci(igor.py): harden _update_file so doesnt fail on nonexistent file
- ci(igor.py): from get_release_facts remove constants repo owner and github url
- ci(igor.py): do_quietly add arg, cwd
- refactor: semantic version separated into separate module
- feat: harden version_semantic handling against version str prepended by v

.. _changes_1-2-31:

Version 1.2.31 — 2024-04-08
---------------------------

- chore(test-coverage.yml): pass in tagged version to build tarball and whl
- test(test_logging_api.py): ci/cd env has both src and build/lib folders. 2x yaml file count
- docs(logging_api.py): class LoggingConfigYaml.__init__ missing one param

.. _changes_1-2-30:

Version 1.2.30 — 2024-04-08
---------------------------

- chore(test-coverage.yml): install logging-strict package before coverage run/report

.. _changes_1-2-29:

Version 1.2.29 — 2024-04-08
---------------------------

- chore: add codecov config file and workflow
- docs(README.rst): show codecov badge

.. _changes_1-2-28:

Version 1.2.28 — 2024-04-08
---------------------------

- docs(pyproject.toml): add homepage and documentation links. pypi.org show links
- docs: inventories updates
- docs: add threat model. Identify sewers; files which are targets for hackers

.. _changes_1-2-27:

Version 1.2.27 — 2024-04-05
---------------------------

- feat: table of contents (toc) seperated from Sphinx rst files
- docs: migrate sphinxcontrib-fulltoc --> sphinx_external_toc
- docs: in toc, link to license. Shows complete license
- docs: in toc, link to github and pypi.org

.. _changes_1-2-26:

Version 1.2.26 — 2024-04-04
---------------------------

- style: minimize usage of typing.Optional and typing.Union
- docs: favor intersphinx_mapping over extlinks. Minimize usage of extlinks
- docs: automodule in use, so module directive create a duplicate. Remove it
- docs: minimize/remove usage of external:[package]+ref:

.. _changes_1-2-25:

Version 1.2.25 — 2024-03-31
---------------------------

- docs(conf.py): intersphinx_mapping set a base url. In inv, paths become relative
- style: black decides add empty line between module header and imports
- chore(pre-commit): update dependency versions
- test: one unittest class name not CamelCase

.. _changes_1-2-24:

Version 1.2.24 — 2024-03-09
---------------------------

- docs: replace references to logging.config.handlers with logging.handlers

.. _changes_1-2-23:

Version 1.2.23 — 2024-03-09
---------------------------

- fix(setup.py): setuptools-scm configuration use setuptools-scm builtin handlers
- docs(setup.py): setuptools-scm docs are sparse. Explain as if to a six year old

.. _changes_1-2-22:

Version 1.2.22 — 2024-03-09
---------------------------

- docs(README.rst): Use raw.githubusercontent.com rather than github.com urls
- fix(README.rst): on rst to epub convert, github.com url showed page, not image

.. _changes_1-2-21:

Version 1.2.21 — 2024-03-02
---------------------------

- docs: resize and clean up validation animation gif

.. _changes_1-2-20:

Version 1.2.20 — 2024-03-02
---------------------------

- docs: add VHS tape. Demonstrate validation animated gif

.. _changes_1-2-19:

Version 1.2.19 — 2024-03-01
---------------------------

- docs: license badge not resolving. Change to github badge

.. _changes_1-2-18:

Version 1.2.18 — 2024-03-01
---------------------------

- docs(README.rst): a badge image url invalid tox -e docs fail

.. _changes_1-2-17:

Version 1.2.17 — 2024-03-01
---------------------------

- docs(README.rst): add badges

.. _changes_1-2-16:

Version 1.2.16 — 2024-03-01
---------------------------

- chore(setup.py): in clean_scheme stop prepending +clean causes readthedocs to fail
- chore(readthedocs): build html and pdf

.. _changes_1-2-15:

Version 1.2.15 — 2024-03-01
---------------------------

- chore(release.yml): jobs can be rerun, protect against publish duplicates
- chore(PyPi): server not configured with environment name

.. _changes_1-2-14:

Version 1.2.14 — 2024-03-01
---------------------------

- chore(TestPyPi): require tagged version, cannot use PEP 440 local versions
- chore(TestPyPi): server not configured with environment name

.. _changes_1-2-14:

Version 1.2.14 — 2024-02-29
---------------------------

- chore(release.yml): separate build from publish and release
- chore(release.yml): run on push, not create
- chore(release.yml): on push publish to test.pypi
- chore(release.yml): on tagged publish to pypi and github releases
- chore(release.yml): use node20 not node16

.. _changes_1-2-13:

Version 1.2.13 — 2024-02-29
---------------------------

- chore(release.yml): configure permissions id-token write
- chore(release.yml): configure environment for pypi
- chore(release.yml): if condition to only run tagged version

.. _changes_1-2-12:

Version 1.2.12 — 2024-02-29
---------------------------

- chore: actions/checkout with fetch-depth 0 gets branches and tags
- chore(release.yml): Publish package using pypa/gh-action-pypi-publish@release/v1

.. _changes_1-2-11:

Version 1.2.11 — 2024-02-28
---------------------------

- chore(ci): in release from on push --> on create tag
- chore(ci): in release fetch tags then get latest commit tag
- chore(ci): in codeql Initialize CodeQL with -> config -> paths and paths-ignore
- chore(ci): in codeql Initialize CodeQL with -> config -> paths folder ok file not ok

.. _changes_1-2-10:

Version 1.2.10 — 2024-02-28
---------------------------

- chore(ci): in testsuite do not download artifacts
- chore(ci): in release get tag name, not branch name. Prevent build create dev wheel
- chore(ci): in codeql limit to src folder tree. Include igor.py and ci/session.py
- chore(ci): in codeql remove from matrix javascript

.. _changes_1-2-9:

Version 1.2.9 — 2024-02-28
--------------------------

- test: tests maybe compiled before run. Cached and non-cached paths' differ
- chore(tox.ini): In lint, remove call, twine check dist/*
- chore: In testsuite and quality, remove prepare which uploaded dist/
- style: fix github repo url in requirements/*.in and docs/*.in

.. _changes_1-2-8:

Version 1.2.8 — 2024-02-27
--------------------------

- fix: build not occurring try to remove igor.py quietly call

.. _changes_1-2-7:

Version 1.2.7 — 2024-02-27
--------------------------

- chore: actions/download-artifact@v3 and actions/upload-artifact@v3 depreciated
- chore: be verbose listing tarballs and wheels


.. _changes_1-2-6:

Version 1.2.6 — 2024-02-27
--------------------------

- chore: move pre-commit to a tox.ini testenv

.. _changes_1-2-5:

Version 1.2.5 — 2024-02-27
--------------------------

- chore: gh workflow prepare dist/*

.. _changes_1-2-4:

Version 1.2.4 — 2024-02-27
--------------------------

- chore(tox.ini): try usedevelop off
- build(pyproject.toml): build as build environment dependency

.. _changes_1-2-3:

Version 1.2.3 — 2024-02-27
--------------------------

- chore(tox.ini): try building tagged version
- fix(release.yml): indention issue

.. _changes_1-2-2:

Version 1.2.2 — 2024-02-27
--------------------------

- fix(tox.ini): lint failing. In testenv build and install package
- chore(ci): release and kit were building develop wheels. Specify tag

.. _changes_1-2-1:

Version 1.2.1 — 2024-02-27
--------------------------

- chore(tox.ini): lint uses twine. Include dependency in dev.in
- chore(tox.ini): mypy needs requirements/mypy.pip
- chore(tox.ini): docs Sphinx warnings removed
- docs: sphinx warnings remove all
- fix(Makefile): REPO_OWNER repository name contains a hyphen
- chore(ci): trigger build kits and download release artifacts
- chore(gh workflows): remove attempt to support macos and windows
- chore(gh workflows): remove python-version pypy-3.8

.. _changes_1-2-0:

Version 1.2.0 — 2024-02-26
--------------------------

- feat: util.pep518_read for reading pyproject.toml sections
- docs(fix): util.pep518_read missing dependency of docs/conf.py
- fix: remove, as much as possible, mentions of package asz beside pyproject.toml sections
- chore(tox.ini): add test target
- chore(tox.ini): suppress noisy package build output
- chore(igor.py): add function do_quietly. suppress a commands noisy output
- docs: add scriv as a dependency
- docs: add logo logging-strict-logo.svg Cleaning svg breaks it. Remove systray-udisk2 logo
- docs: create sphinx object inventories to minimize sphinx build warnings
- docs: query sphinx object inventory using sphobjinv rather than sphinx.ext.intersphinx
- chore(ci): add .readthedocs.yml config file
- chore: add tox/ and cheats.txt to .gitignore
- chore(ci): add many .github/workflows
- chore(ci): add Makefile ci targets. add clean and sterile targets

.. _changes_1-1-0:

Version 1.1.0 — 2024-02-23
--------------------------

- docs: sphinx docs. user and code manual
- docs: Versioning explanation and howto
- feat: add tech_niques.stream_capture.CaptureOutput
- refactor: remove constants.RICH_OVERFLOW_OPTION_DEFAULT
- chore(igor.py): kind can now be a version str

.. _changes_1-0-1:

Version 1.0.1 — 2024-02-20
------------------------------------------------

- fix: retire public API function, setup_ui
- docs: Example code reflect correct API function calls

.. _changes_1-0-0:

Version 1.0.0 — 2024-02-20
------------------------------------------------

- style: isort and whitespace removal
- docs: correct module header dotted path
- docs: module exports update
- feat!: API contains public methods, enum, and exceptions
- docs: public API
- docs: example code for both UI and worker
- fix!: retire public API function, setup_worker
- fix: split setup_worker into two seperate steps. extract+validate and setup

.. _changes_0-1-1:

Version 0.1.1 — 2024-02-19
------------------------------------------------

In unittests, track down export of `*.worker.logging.config.yaml` to xdg user data dir,
rather than to a temp folder. To test, monitor ~/.local/share/[prog name] unlink
anything in that folder. Run, make coverage. The folder should remain empty

- test: prevent/redirect export of *.worker.logging.config.yaml to temp folder

.. _changes_0-1-0:

Version 0.1.0 — 2024-02-19
------------------------------------------------

- chore(setuptools-scm): semantic versioning. See constants.py, _version.py, and igor.py

- chore(isort): support extensions py and pyi

- chore(pre-commit): local repo bypasses hook. Once published local repo config unnecessary

- feat(pre-commit): hook validate-logging-strict-yaml

- feat: within a folder tree, use a pattern to extract package data files

- feat: validate logging.config yaml. Entrypoint logging_strict_validate_yaml

- feat(tech_niques): add context_locals

- feat(tech_niques): add logging_capture

- feat(tech_niques): add logging_redirect

- feat(tech_niques): add coverage_misbehaves. Detect if runner is coverage

- feat(tech_niques): add inspect a class interface

- feat: add two logging.config yaml files. One for app. One for worker

- test: add two dummy logging.config yaml files. One for app. One for worker

- feat(appdirs): package appdirs support. Chooses correct xdg folder

.. scriv-end-here
