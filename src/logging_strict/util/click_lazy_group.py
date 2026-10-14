"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

**Nested pattern**

LazyGroup (top)
  └── lg    -->  cli            (group)
                    └── thecmd  (command)

$> :code:`cli lg thecmd`

- cli -- For illustration, (pretend) entrypoint name, not the `click.group` name.

- lg  -- The point/goal is to import less code.

         :code:`lazy_subcommands={"lg": "mypkg.mysubpackage.lg"}`

         Mimics pyproject.toml [project.scripts] structure. Python users should
         already be familiar with `LazyGroup.lazy_subcommands` usage.

         Your click entrypoint module will likely contain multiple subcommands.
         This is how to choose one click subcommand without importing
         modules of other subcommands. The dict `LazyGroup.lazy_subcommands`
         controls the routing.

         ``lg`` is an example key to, retrieve the value
         (from `LazyGroup.lazy_subcommands`), the module import dotted path.
         That module and respective click subcommand is imported.

- thecmd -- your click subcommand from decorator ``@cli.command(name="thecmd")``
            or if name not provided, the click subcommand function
            name, e.g. ``run_thecmd``.

Nested example in:

- ``tests/test_click_lazy_group.py::TestLazyCall:test_nested_pattern``

- ``tests/cli/lg.py``

  Module contains a `click.group` and one or more `group.command`.

**Flat pattern**

LazyGroup (top)
  ├── build -->  build_cmd      (command)
  ├── test  -->  test_cmd       (command)
  └── check -->  check_cmd      (command)

$> :code:`cli build --sdist`

One extra hop in nested. Returns whatever object the dotted path points to.
Click handles both.

**Flat example**

Entrypoint module

.. code-block:: text

   import click
   from logging_strict.util.click_lazy_group import LazyGroup

   @click.group(
       cls=LazyGroup,
       lazy_subcommands={
           "build": "wreck.commands.build:build_cmd",
           "test":  "wreck.commands.test:test_cmd",
           "check": "wreck.commands.check:check_cmd",
       },
       context_settings={"help_option_names": ["-h", "--help"]},
   )
   def cli():
       # entrypoint func name, which is usually main, not cli.
       pass

Flat example in:

- ``tests/test_click_lazy_group.py::TestLazyCall:test_flat_pattern``

- ``tests/cli/cmds_build.py``

  Module contains one `group.command`.

Example command module

.. code-block:: text

   @click.command(name="build")
   @click.option("--sdist", is_flag=True, help="Build an sdist")
   @click.option("--wheel", is_flag=True, help="Build a wheel")
   @click.option("--outdir", type=click.Path(), default="dist", show_default=True)
   def build_cmd(sdist: bool, wheel: bool, outdir: str) -> None: ...

.. seealso::

   Unmaintained package :pypi_org:`click-lazy`. But without redundant
   cached_property layer.



"""

import importlib

import click

__all__ = ("LazyGroup",)


class LazyGroup(click.Group):  # type: ignore[misc,unused-ignore]
    """click subcommands live in their own module. Only the subcommand being
    used will be imported.

    :ivar lazy_subcommands: command name and respective import dotted path
    :vartype lazy_subcommands: dict[str, str] | None
    """

    def __init__(
        self,
        *args,
        lazy_subcommands=None,
        **kwargs,
    ) -> None:
        """Adds attribute, lazy_subcommands"""
        super().__init__(*args, **kwargs)
        self.lazy_subcommands = lazy_subcommands or {}

    def list_commands(self, ctx):
        """registered but not imported commands

        :type ctx: click.Context
        :rtype: list[str]
        """
        base = super().list_commands(ctx)
        ret = base + sorted(self.lazy_subcommands)
        return ret

    def get_command(self, ctx, cmd_name):
        """Extends click get_command

        :type ctx: click.Context
        :type cmd_name: str
        :rtype: click.Command | None
        """
        if cmd_name in self.lazy_subcommands:  # pragma: no branch
            mod_dotted_path, objname = self.lazy_subcommands[cmd_name].rsplit(":", 1)
            cmd = getattr(importlib.import_module(mod_dotted_path), objname)
            if not isinstance(cmd, click.Command):  # pragma: no branch
                msg_warn = f"Lazy load of {cmd_name} returned non-Command"
                raise ValueError(msg_warn)
            # cache
            self.commands[cmd_name] = cmd
        ret = super().get_command(ctx, cmd_name)
        return ret
