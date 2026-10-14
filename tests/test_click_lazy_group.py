"""
Pulled straight from package ``click-lazy`` to avoid reinventing the wheel.

https://raw.githubusercontent.com/nagolos/click-lazy/refs/heads/main/tests/test_unit.py

"""

import unittest

from logging_strict.util.package_resource import is_package_exists


def setUpModule() -> None:
    """Quit quickly. Missing optional dependencies, e.g. click.
    click has some rich features, but LazyGroup not using those
    """
    t_optional_dependencies = ("click",)
    missing = [pkg for pkg in t_optional_dependencies if not is_package_exists(pkg)]
    if missing:
        msg_warn = f"optional deps missing: {', '.join(missing)}"
        raise unittest.SkipTest(msg_warn)


class TestLazy(unittest.TestCase):
    """Test LazyGroup"""

    def test_lazygroup_list_commands(self) -> None:
        """list_commands commands within module."""
        import click

        from logging_strict.util.click_lazy_group import LazyGroup

        lazy_subcommands = {"lg": "tests.cli.lg:cli"}
        lg = LazyGroup(
            lazy_subcommands=lazy_subcommands,
            help="Group to import",
        )

        # Step 1: the lazy subcommand name is listed
        commands = lg.list_commands(ctx=None)
        self.assertIn("lg", commands)

        # Step 2: resolve it and check its subcommands
        ctx = click.Context(lg)
        cmd_name = "lg"
        resolved_0 = lg.get_command(ctx, cmd_name)
        self.assertIn("thecmd", resolved_0.list_commands(ctx))

        # no such cmd --> None
        #    click `Group.resolve_command` --> lg.get_command --> None --> NoSuchCommand
        cmd_name_bool = "nosuchcmd"
        resolved_1 = lg.get_command(ctx, cmd_name_bool)
        self.assertIsNone(resolved_1)

        # target is not a click.Command --> ValueError
        lazy_subcommands_1 = {"lg": "logging_strict.util.package_resource:check_folder"}
        lg_1 = LazyGroup(
            lazy_subcommands=lazy_subcommands_1,
            help="Group to import",
        )
        ctx_1 = click.Context(lg_1)
        with self.assertRaises(ValueError):
            lg_1.get_command(ctx_1, cmd_name)


class TestLazyCall(unittest.TestCase):
    """Test call cli command."""

    def test_nested_pattern(self) -> None:
        """Call the entrypoint"""
        import sys

        import click  # noqa: F401
        from click.testing import CliRunner

        from logging_strict.util.click_lazy_group import LazyGroup

        # No click.Group() wrapper needed
        # LazyGroup -- CLI entry point
        # lg        -- lazily-loaded subcommand
        # thecmd    -- lives inside that resolved group
        lazy_subcommands = {"lg": "tests.cli.lg:cli"}
        cl = LazyGroup(
            lazy_subcommands=lazy_subcommands,
            help="Group to import",
        )

        runner = CliRunner()
        result = runner.invoke(cl, ["lg", "thecmd"])

        # Debug: see the actual error
        if result.exit_code != 0:
            print(result.output, file=sys.stderr)
            print(result.exception, file=sys.stderr)

        self.assertEqual(result.exit_code, 0)

        from tests.cli import lg

        res = getattr(lg.run_thecmd, "_called", False)
        self.assertTrue(res)

    def test_flat_pattern(self) -> None:
        """Call the entrypoint"""
        import sys

        import click  # noqa: F401
        from click.testing import CliRunner

        from logging_strict.util.click_lazy_group import LazyGroup

        # No click.Group() wrapper needed
        # LazyGroup -- CLI entry point
        # lg        -- lazily-loaded subcommand
        # thecmd    -- lives inside that resolved group
        lazy_subcommands = {"build": "tests.cli.cmds_build:build_cmd"}
        cl = LazyGroup(
            lazy_subcommands=lazy_subcommands,
            help="Each module contains one click.Command. Minimizes import surface",
        )

        runner = CliRunner()
        # flat pattern -- click entrypoint module contains only one command
        result = runner.invoke(cl, ["build", "--sdist"])

        # Debug: see the actual error
        if result.exit_code != 0:
            print(result.output, file=sys.stderr)
            print(result.exception, file=sys.stderr)

        self.assertEqual(result.exit_code, 0)

        from tests.cli import cmds_build

        res = getattr(cmds_build.build_cmd, "_called", False)
        self.assertTrue(res)


if __name__ == "__main__":  # pragma: no cover
    """Without coverage

    .. code-block:: shell

       python -m tests.test_click_lazy_group

    """
    unittest.main(tb_locals=True)
