Validation
===========

logging.handlers, each, expects parameters to have the correct data type.

yaml package strictyaml, default data type is str, for other types, the function
variable name and type must be known (and supported) beforehand.

For custom (handlers, filters, and formatters) functions, there is no
way to know beforehand the parameter name **and therefore** the data type,
parameter type will become str

Validate a logging.config.yaml file
------------------------------------

Assuming the virtual environment is activated

- Within source code (tree)

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

- Within xdg user data dir

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

- Within a package

.. code:: console

   logging_strict_validate_yaml $HOME/Downloads/logging_strict/src/logging_strict/configs

Processed: 4 / 4
Success / fail: 4 / 0
last (0): ~/Downloads/logging_strict/src/logging_strict/mp_1_asz.worker.logging.config.yaml

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

Curated files
--------------

Which :py:mod:`logging.config` yaml files are in the package?

Should a hunting party be organized and how many horses and muskets
will need to be mustered?

Ouch!

There is no command, instead here's a list:

- textual_1_asz.app.logging.config.yaml

  For use with a textual console app.

  Handler: textual.handlers.TextualHandler

- mp_1_asz.worker.logging.config.yaml

  For use with :py:class:`multiprocessing.pool.Pool` workers

  Handler: logging.StreamHandler
