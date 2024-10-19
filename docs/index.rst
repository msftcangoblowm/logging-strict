.. Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
.. For details: https://github.com/msftcangoblowm/logging-strict/blob/master/NOTICE.txt

logging_strict
===============

.. _index-overview:

Overview
---------

logging.config yaml Strict typing and editable

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

  The schema is specifically tailored for the :py:mod:`logging.handlers`

  As long as the yaml is valid, will have the data types
  :py:mod:`logging.handlers` expect

- exports package data

  Alternative to :py:func:`pkgutil.get_data`

  Export data files using a pattern rather than one file at a time


The latest version is |project_name| |release|.  It is supported on:

- py39 - py313
- CPython and pypy
- MacOS Windows and Linux

Why?
------

logging.config is more often than not hardcoded within a package's
source code. Removing logging.config from the source code and into
an exported yaml config file, exported files are edittable. With added
benefit can quickly adapt to unforeseen unexpected bleeding of logging
messages.

When a bleed occurs, open the exported logging.config yaml file. Add
the offending package to the ``loggers`` section or if already there,
increase the logging level.

For example, for asyncio, adjust logging level from
logging.WARNING --> logging.ERROR

Bye bye disruptive informational logging warning messages.

logging_strict comes with a logging.config yaml validator. So can
check the editted yaml file.

On app|worker restart, the logging configuration changes take effect.

Quick start
-----------

Getting started is easy:

From your packages project base folder. This example assumes, unittests folder, ``tests/``

#. Install |project_name|::

    $ . [venv path]/activate
    $ python3 -m pip install logging_strict

:doc:`For full details </getting_started/install>`

.. tableofcontents::

.. only:: html

   * :ref:`genindex`

   * :ref:`modindex`

   * :ref:`search`
