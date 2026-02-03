"""Rose CLI - run with: python -m rose"""

import typer
from rose.command_framework import VERSION
from rose.command_framework.command_index import CommandIndex
from rose.command_framework.constants import PROJECT_DIR


app = typer.Typer(
    no_args_is_help=True,
    rich_markup_mode="markdown",
    help=open(PROJECT_DIR / "SKILL.md").read(),
    add_completion=False,
    add_help_option=False,
)


@app.command()
def version() -> None:
    """Show version."""
    typer.echo(f"Rose {VERSION}")


COMMAND_INDEX = CommandIndex()
for command in COMMAND_INDEX.commands.values():
    function = command.command.call
    function.__doc__ = command.command.description
    app.command(
        f"{command.name}",
        help=command.command.skill_markdown,
    )(function)
    

if __name__ == "__main__":
    app()
