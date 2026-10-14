"""
.. moduleauthor:: Alexander Kulikov <https://github.com/nagolos/click-lazy>

**Nested pattern**

Module contains a `click.group` and one or more `group.command`.

.. code-block:: text

   LazyGroup (top)
     └── lg    -->  cli            (group)
                       └── thecmd  (command)

.. seealso::

   This test module from package ``click-lazy`` testsuite.
   :github_repo:`nagolos/click-lazy` License: Apache-2.0

   :py:mod:`LazyGroup docs <logging_strict.util.click_lazy_group>`_

"""

import click

cmd_called = False


@click.group()
def cli() -> None:
    """This script"""


@cli.command(name="thecmd")
def run_thecmd() -> None:
    """Nested pattern. Module contains a click.group and group command(s)"""
    global cmd_called
    cmd_called = True

    run_thecmd._called = True
