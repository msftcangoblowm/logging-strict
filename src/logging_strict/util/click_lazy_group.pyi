from typing import Any

import click

__all__ = ("LazyGroup",)

class LazyGroup(click.Group):  # type: ignore[misc,unused-ignore]
    lazy_subcommands: dict[str, str]

    def __init__(
        self,
        *args: Any,
        lazy_subcommands: dict[str, str] | None = ...,
        **kwargs: Any,
    ) -> None: ...
    def get_command(
        self, ctx: click.Context, cmd_name: str
    ) -> click.Command | None: ...
    def list_commands(self, ctx: click.Context) -> list[str]: ...
