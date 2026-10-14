"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

LazyGroup Flat pattern

"""

import click

cmd_called = False


@click.command(name="build")
@click.option("--sdist", is_flag=True, help="Build an sdist")
@click.option("--wheel", is_flag=True, help="Build a wheel")
@click.option("--outdir", type=click.Path(), default="dist", show_default=True)
def build_cmd(sdist: bool, wheel: bool, outdir: str) -> None:
    """One module one click.Command"""
    global cmd_called
    cmd_called = True

    build_cmd._called = True
