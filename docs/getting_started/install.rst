.. _install_overview:

Overview
================

.. _whats_in_package:

What's in |project_name|
-------------------------

|project_name| primary focus is on logging.config yaml. Quick breakdown of other useful tidbits.

tech_niques
~~~~~~~~~~~~

- async and sync logging howto

- logging capture

- When writing unittest, see more indepth locals

helpers
~~~~~~~~

- extract package data using a pattern, rather than one at a time

Alternative to :py:mod:`pkgutil`

- validate logging.config yaml files (entrypoint and pre-commit hook)

- xdg_folders

Alternative to appdirs

.. _getting_started:

Getting Started
================

.. _install_activate_venv:

Activate venv
-------------

.. code-block:: shell

   . [venv path]/bin/activate


.. _install_dependencies_from_pypi_org:

Install -- production (pypi.org)
---------------------------------

Install |project_name| package

.. code-block:: shell

   pip install --upgrade logging_strict

.. _install_dependencies_from_source:

Install -- production (source code)
------------------------------------

Download tarball and uncompress into a folder, cwd to that folder. checkout
a tagged version

.. code:: shell

   python igor.py build_next "[tagged version]"
   make install-force

.. _install_optional_dependencies_pypi_org:

Install -- optional (pypi.org)
---------------------------------

ui -- will install the dependencies for the UI

.. code:: shell

   pip install --upgrade logging_strict[pip]
   pip install --upgrade logging_strict[pip_tools]
   pip install --upgrade logging_strict[manage]
   pip install --upgrade logging_strict[dev]
   pip install --upgrade logging_strict[docs]

or, for strict control, sync venv with piptools

.. code:: shell

   pip-sync requirements/prod.pip requirements/manage.pip docs/requirements.pip requirements/dev.pip

.. _install_optional_dependencies_from_source:

Install -- optional (source code)
---------------------------------

.. code:: shell

   pip install --upgrade -r requirements/manage.pip
   pip install --upgrade -r requirements/prod.pip
   pip install --upgrade -r requirements/dev.pip
   pip install --upgrade -r docs/requirements.pip

.. _install_whats_next:

Whats next
~~~~~~~~~~~

Now it's time to :ref:`integrate <getting_started/usage:app integration>` |project_name| with your app
