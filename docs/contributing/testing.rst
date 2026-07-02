Testing
========

Why unittest?
--------------

Tests are written for unittest, not pytest. It's not for lack of skill;
would be easy to migrate. That it's not migrated is a curiousity. That
it's never going to be migrated is a head scratcher.

Huh?

There is an unpublished package, ``asz``. It's a terminal UI that runs
tests in parallel. Uses multiprocessing. Rather than always running the
entire testsuite, run only the tests for (code) modules which have changes.

- Dramatically reduces time spent waiting for test suite to complete.

- Encourages keeping tests organized by (code) module(s).

``asz`` only supports unittest, not pytest. Even after ``asz`` implements
pytest support, ``asz`` would prefer |project_name| to keep tests exclusively
written with unittest.

Run tests
----------

Entire testsuite
~~~~~~~~~~~~~~~~~

During development or pressed for time.

.. code-block:: shell

   make check

In tox
~~~~~~~

tox must be used before creating a commit.

.. code-block:: shell

   rm -rf build/lib; cd .tox && tox --root=.. -c ../tox-test.ini -e py312-linux --workdir=.; cd - &>/dev/null

This command can be found in ``tox-test.ini``. Just Ctrl+P into the terminal.
