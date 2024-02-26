app integration
================

.. _configure_when_not_required:

Lets discuss integrating |project_name| into your app and history
dust binning hardcoded logging configuration.

app
----

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~

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
--------------

This is a 2 step process.

- Step 1 -- entrypoint

  Extracts yaml from package, validates, then passes as str to the worker process

- Step 2 -- worker

  yaml str --> logging.config.dictConfig

within entrypoint
~~~~~~~~~~~~~~~~~~

The :py:class:`multiprocessing.pool.Pool` (not ThreadPool) worker is
isolated within it's own process. So the dirty nature of logging
configuration has no effect on other processes.

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

entrypoint passes str_yaml to the (:py:class:`multiprocessing.pool.Pool`)
worker. A worker calls `setup_logging_yaml` with the yaml str

.. code:: text

   from logging_strict import setup_logging_yaml

   setup_logging_yaml(str_yaml)


To learn more about building UI apps that have :py:class:`multiprocessing.pool.Pool`
workers, check out the `asz` source code

Whats next
-----------

- :ref:`Public API <code/public_api/index:public api>`

- :ref:`howto - Validate YAML files <getting_started/validation:validation>`
