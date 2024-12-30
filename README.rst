.. Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
.. For details: https://github.com/msftcangoblowm/logging-strict/blob/master/NOTICE.txt

logging-strict
===============

logging.config yaml Strict typing and editable

|  |kit| |license| |versions|
|  |test-status| |codecov| |quality-status| |docs|
|  |stars| |mastodon-msftcangoblowm|

For logging.config yaml files, logging-strict does the following:

- Editable logging configuration

  While running a Python app, some arbritary package, out of no
  where, decides to log an informational warning. Within a multiprocessing
  worker (aka heavy background processing), these logging warnings go
  from annoying --> disruptive.

  The best can do is *adapt to survive*. Make this situation quickly
  solvable by adjusting the app's logging configuration.

  asyncio is an example package which bleeds informational logging warnings

- curates

  Intention is to have all the valid logging.config yaml in one place

- validator

  logging_strict comes with a logging.config yaml validator. So can
  check the editted yaml file. Supports pre-commit

- validates against a strictyaml schema

  The schema is specifically tailored for the logging.handlers

  As long as the yaml is valid, will have the data types
  logging.handlers expect

- exports package data

  Alternative to pkgutil.get_data

  Export data files using a pattern rather than one file at a time

.. PYVERSIONS

* Python 3.9 through 3.12, and 3.13.0a3 and up.

**New in 1.4.x:**

yaml logger package_name placeholder; noninstalled package raise ImportError;
fix package name to valid dotted path (#3);

**New in 1.3.x:**

resolve dependency conflict by pinning python-dateutil;
fix pwd and shutil.chown are non-Windows; Windows MacOS Pypy py313 support;

Why?
------

logging.config is more often than not hardcoded within a package's
source code. Removing logging.config from the source code and into
an exported yaml config file, a package becomes adaptable to
unforeseen unexpected bleeding of logging messages.

When a bleed occurs, open the exported logging.config yaml file. Add
the offending package to the ``loggers`` section or if already there, increase
the logging level.

For example, for asyncio, adjust logging level from
logging.WARNING --> logging.ERROR

Bye bye disruptive informational logging warning messages.

logging_strict comes with a logging.config yaml validator. So can
check the editted yaml file.

On app|worker restart, the logging configuration changes take effect.

Exporting -- when
------------------

Exports occur before the logging.config yaml files are needed. There
are two process types: worker and app

When an app is run, it exports the app logging configuration.

Right before a ProcessPool runs, it exports the worker logging configuration.

Right before a thread or ThreadPool runs, G'd and Darwin sit down to decide
which calamity will befall you. Best to avoid that cuz Python logging module is
thread-safe. Changes to the logging.config in one thread affects them all
and those changes last as long as the app runs.

Safe means safe to remove you from the gene pool. Would be a great name for a
horror movie. Don't be in that movie.

Exporting -- where/what
------------------------

Export location (on linux): ``$HOME/.local/share/[package name]/``

This is xdg user data dir and the configuration is per package.
Python logging configurations' cascade!

Whats exported?

- one for the app

- At least one, for the multiprocessing workers

If a user|coder edits and makes a change, undo'ing those changes would be
considered quite rude, minimally, poor ettiquette.

So that gauntlets stay on and package authors live long fulfilling peaceful
uneventful lives, overwrite existing logging config yaml files never
happens. Although fully capable, just absolutely refuses to do so!

If confident no changes have been made, can manually delete (unlink).

There will be no need for gauntlets, can safely put those away.

Upgrade path
--------------

*How to upgrade a particular logging.config yaml file?*

Best to increment the version and switch the code base to use the latest version

Custom changes should be upstreamed.

*Preferred the previous version*

There currently isn't a means to change which logging.config yaml file
a package uses.

This sounds like a job for user preference database, gschema. Not yet
implemented

Validation
-----------

logging.handlers, each, expects parameters to have the correct data type.

yaml package strictyaml, default data type is str, for other types, the function
variable name and type must be known (and supported) beforehand.

For custom (handlers, filters, and formatters) functions, there is no
way to know beforehand the parameter name **and therefore** the data type,
parameter type will become str

(Assuming the virtual environment is activated)

Within source code (tree)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. image:: https://raw.githubusercontent.com/msftcangoblowm/logging-strict/master/docs/_static/validate_flavor_asz.gif
   :alt: validation of package logging.config yaml files
   :width: 1000px
   :height: 500px

.. code:: console

   logging_strict_validate_yaml

.. code:: text

   Processed: 4 / 4
   Success / fail: 4 / 0
   last (3): ~/Downloads/logging_strict/src/logging_strict/configs/mp_1_asz.worker.logging.config.yaml

.. code:: console

   logging_strict_validate_yaml --category worker

.. code:: text

   Processed: 3 / 3
   Success / fail: 3 / 0
   last (2): ~/Downloads/logging_strict/src/logging_strict/configs/mp_1_asz.worker.logging.config.yaml

.. code:: console

   logging_strict_validate_yaml --category app

.. code:: text

   Processed: 1 / 1
   Success / fail: 1 / 0
   last (0): ~/Downloads/logging_strict/src/logging_strict/configs/textual_1_asz.app.logging.config.yaml

.. note:: Two workers are just ordinary yaml files

   Withinin logging_strict source tree, `bad_idea/folder*/*` are two folders,
   each contains one file.

   Although valid yaml, these are not actual logging.config yaml files.
   Just there for testing purposes

   The total `*.logging.config.yaml` file count and total
   `*.worker.logging.config.yaml` are both thrown off by `+2`

Within xdg user data dir
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: console

   logging_strict_validate_yaml $HOME/.local/share/logging_strict/ worker

Processed: 1 / 1
Success / fail: 1 / 0
last (0): ~/.local/share/logging_strict/mp_1_asz.worker.logging.config.yaml

.. code:: console

   logging_strict_validate_yaml $HOME/.local/share/logging_strict/ app

Processed: 1 / 1
Success / fail: 1 / 0
last (0): ~/.local/share/logging_strict/textual_1_asz.app.logging.config.yaml

pre-commit
------------

Locally

.. code:: text

   repos:
     - repo: local
       hooks:
         - id: validate-logging-config-yaml
           name: validate-logging-config-yaml
           entry: logging_strict_validate_yaml
           language: python
           require_serial: true
           pass_filenames: false

Normal usage

.. code:: text

   repos:
     - repo: https://github.com/msftcangoblowm/logging-strict
       rev: 0.1.0
       hooks:
         - id: validate-logging-config-yaml
           name: validate-logging-config-yaml
           entry: logging_strict_validate_yaml
           language: python
           require_serial: true
          pass_filenames: false

install
--------

You know how to use pip. This is not that.

Lets discuss integrating logging-strict into your app and history
dust binning hardcoded logging configuration.

UI
~~~

An entrypoint boilerplate should be structured like, or slightly
differently for an async app

.. code:: text

   def _process_args(): ...

   def main():
       d_out = _process_args()
       ...
       # app logging config stuff <--- here!
       app = MyApp()  # <-- not within here
       ...

   if __name__ = "__main__":
       main()

This entrypoint is testable. If the argparsing is done within main,
it's time to refactor and rework the entrypoint.

An Entrypoint have defined and **documented** exit codes. Besides for
``--help|-h``, never prints a message

logging.config yaml -- within logging_strict
"""""""""""""""""""""""""""""""""""""""""""""

.. code:: text

   from logging_strict.constants import
   from logging_strict import ui_yaml_curated, LoggingState

   genre = "textual"
   version_no = "1"
   flavor = "asz"  # < -- Yet unpublished testing UI package
   package_start_relative_folder = ""

   LoggingState().is_state_app = True
   ui_yaml_curated(
       genre,
       flavor,
       version_no=version_no,
       package_start_relative_folder=package_start_relative_folder,  # <-- narrows the search
   )

logging.config yaml -- within another package
""""""""""""""""""""""""""""""""""""""""""""""

.. code:: text

   from mypackage.constants import urpackagename, package_data_folder_start
   from logging_strict import setup_ui_other, LoggingState

   genre = "textual"
   flavor = "asz"  # < -- Yet unpublished testing UI package
   version_no = "1"
   package_start_relative_folder = ""

   LoggingState().is_state_app = True
   setup_ui_other(
       urpackagename,  # <-- Would have been better to curate within logging_strict
       package_data_folder_start,
       genre,
       flavor,
       version_no=version_no,
       package_start_relative_folder=package_start_relative_folder,
   )

- package

  Package within which the `*.[app|worker].logging.config.yaml` files
  reside.

  Which is preferrably within logging_strict. So all the logging.config yaml
  in the universe need not be duplicated to the point where it appears
  to compete with fiat currency.

- package_data_folder_start

  Within that package, which is the package base folder somewhere
  within the folder tree lies the `*.[app|worker].logging.config.yaml`
  files. This is a str, not a relative path.

  One folder name. Does not assume the folder is called ``data``. Does assume
  data files are within at least one folder. And if not? G'd and Darwin. Or
  panties are bound to get twisted.

- category

  The function name indicates the purpose. To setup ``logging.config`` for
  a worker, call function, ``setup_worker``

- genre

  From a main app's POV, genre is the UI framework such as: pyside or textual

  From a worker's POV, genre hints at the implementation:
  mp (multiprocessing) or rabbitmq, ...

- flavor

  Like a one word brand name to a particular logging.config yaml file. For the
  initially used the brand, ``asz``, a Python testing UI app

- version_no

  When changes have to be made either: Increment
  the version by 1 or if purpose is different, fork a new flavor

  If no flavor, version pertains to the genre

- package_start_relative_folder

  Relative to package_data_folder_start, narrows search.

  For example,

  ``bad_idea/folder0/`` and ``bad_idea/folder1`` both contains,
  ``mp_1_shared.worker.logging.config.yaml``. Which one?

  package_data_folder_start is ``bad_idea``, not ``configs`` or ``data``.
  package_start_relative_folder could be ``folder0``. Which is enough
  to identify the exact file.

LoggingState
"""""""""""""

A Singleton holding logging state. To know whether or not, run by app
or from cli

(there is also the issue of run by: coverage, unittest, or pytest)

If run from app, and testing app component, logging is redirected to
`textual.logging.TextualHandler` and shouldn't be changed.

If run from cli, and testing app component, logging is redirected to
`logging.handlers.StreamHandler`, not TextualHandler

During testing, the app and workers are run in all three scenerios.

From coverage, from unittest, and from asz.

While the logging handler is TextualHandler, changing to StreamHandler
would be bad. LoggingState aim is to avoid that.

Why would want to do testing from an UI?

- **Speeeeeeeeeed!**

Minimizing keypresses or actions required to run commands

- Associating unittests to code modules

Which unittest(s) must be run to get 100% coverage for a particular
code module?

Without organization, can only imagine that there must always be a 1:1
ratio between unittest and code module. And if not, the unittests
folder is just a jumbled mess. And which unittests matter for a
particular code module is unknown.

**Give a brother a clue!**

A clear easily maintainable verifiable guide is necessary.

worker
-------

This is a 2 step process.

- Step 1 -- entrypoint

  Extracts yaml from package, validates, then passes as str to the worker process

- Step 2 -- worker

  yaml str --> logging.config.dictConfig

within entrypoint
~~~~~~~~~~~~~~~~~~

The ProcessPool (not ThreadPool) worker is isolated within it's own
process. So the dirty nature of logging configuration has no effect
on other processes.

logging.config yaml file within package, logging_strict

.. code:: text

   from logging_strict import worker_yaml_curated

   genre = "mp"
   flavor = "asz"

   str_yaml = worker_yaml_curated(genre, flavor)

logging.config yaml file within another package

.. code:: text

   from logging_strict import worker_yaml_curated

   package = "someotherpackage"
   package_data_folder_start = "data"  # differs so need to check this folder name

   genre = "mp"
   flavor = "asz"

   str_yaml = setup_worker_other(package, package_data_folder_start, genre, flavor)


within worker
~~~~~~~~~~~~~~

entrypoint passes str_yaml to the (ProcessPool) worker. A worker calls
`setup_logging_yaml` with the yaml str

.. code:: text

   from logging_strict import setup_logging_yaml

   setup_logging_yaml(str_yaml)


To learn more about building UI apps that have `multiprocessing.pool.ProcessPool`
workers, check out the `asz` source code

Public API
-----------

.. code:: text

   from logging_strict import (
      LoggingConfigCategory,
      LoggingState,
      LoggingYamlType,
      setup_ui_other,
      ui_yaml_curated,
      setup_worker_other,
      worker_yaml_curated,
      setup_logging_yaml,
      LoggingStrictError,
      LoggingStrictPackageNameRequired,
      LoggingStrictPackageStartFolderNameRequired,
      LoggingStrictProcessCategoryRequired,
      LoggingStrictGenreRequired,
   )

- LoggingConfigCategory

  tl;dr; ^^ won't need this ^^

  Process categories Enum. Iterate over the Enum values, using class
  method, `categories`.

  `strict_logging` public methods are convenience functions for class,
  `strict_logging.logging_api.LoggingConfigYaml`. If LoggingConfigYaml
  used directly, choose one of the LoggingConfigCategory values to
  pass as param, category.

- LoggingYamlType

  tl;dr; ^^ won't need this ^^

  Useful only during strict type checking. class LoggingConfigYaml
  implements LoggingYamlType interface and is a direct subclass

- LoggingStrictError

  logging_strict catch all Exception. Base type of other exceptions.
  Implements ValueError

  The other exceptions are self explanatory. When creating worker
  entrypoints, can set exit codes based on which exception occurred.

Whats strictyaml?
------------------

Unfortunately yaml spec is too broad, allowing undesirable complexity, which
are a frequent cause of security issues. Read more:

- `[why] <https://hitchdev.com/strictyaml/why/>`_

- `[why nots] <https://hitchdev.com/strictyaml/why-not/>`_

strictyaml (`[docs] <https://hitchdev.com/strictyaml/>`_) mitigates
yaml security issues:

- by only supporting a subset of the yaml spec

- type-safe YAML parsing and validation against a schema

  In our case, specialized to support the built-in Python
  logging.handlers and adaptable enough to support custom
  handlers, filters, and formatters

.. |test-status| image:: https://github.com/msftcangoblowm/logging-strict/actions/workflows/testsuite.yml/badge.svg?branch=master&event=push
    :target: https://github.com/msftcangoblowm/logging-strict/actions/workflows/testsuite.yml
    :alt: Test suite status
.. |quality-status| image:: https://github.com/msftcangoblowm/logging-strict/actions/workflows/quality.yml/badge.svg?branch=master&event=push
    :target: https://github.com/msftcangoblowm/logging-strict/actions/workflows/quality.yml
    :alt: Quality check status
.. |docs| image:: https://readthedocs.org/projects/logging-strict/badge/?version=latest&style=flat
    :target: https://logging-strict.readthedocs.io/
    :alt: Documentation
.. |kit| image:: https://img.shields.io/pypi/v/logging-strict
    :target: https://pypi.org/project/logging-strict/
    :alt: PyPI status
.. |versions| image:: https://img.shields.io/pypi/pyversions/logging-strict.svg?logo=python&logoColor=FBE072
    :target: https://pypi.org/project/logging-strict/
    :alt: Python versions supported
.. |license| image:: https://img.shields.io/github/license/msftcangoblowm/logging-strict
    :target: https://pypi.org/project/logging-strict/blob/master/LICENSE.txt
    :alt: License
.. |stars| image:: https://img.shields.io/github/stars/msftcangoblowm/logging-strict.svg?logo=github
    :target: https://github.com/msftcangoblowm/logging-strict/stargazers
    :alt: GitHub stars
.. |mastodon-msftcangoblowm| image:: https://img.shields.io/mastodon/follow/112019041247183249
    :target: https://mastodon.social/@msftcangoblowme
    :alt: msftcangoblowme on Mastodon
.. |codecov| image:: https://codecov.io/gh/msftcangoblowm/logging-strict/graph/badge.svg?token=HCBC74IABR
    :target: https://codecov.io/gh/msftcangoblowm/logging-strict
    :alt: logging-strict coverage percentage
