"""Rose CLI - run with: python -m rose"""

import os
import typer

from rose.command_framework import VERSION
from rose.command_framework.command_index import CommandIndex
from rose.command_framework.constants import PROJECT_DIR

DEFAULT_FILES = {
    "commands.index": "create_command\nenvironment_variables\ninstall\n",
    "requirements.txt": "",
    ".env": "",
    "saved_variables.json": "{}",
}


app = typer.Typer(
    no_args_is_help=True,
    rich_markup_mode="markdown",
    help=open(PROJECT_DIR / "SKILL.md").read(),
    add_completion=False,
    add_help_option=False,
)


# Create required files
for file, content in DEFAULT_FILES.items():
    file_path = os.path.join(PROJECT_DIR, file)
    if not os.path.exists(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            f.write(content)


@app.command()
def version() -> None:
    """Show version."""
    typer.echo(f"Rose {VERSION}")


COMMAND_INDEX = CommandIndex()
for command in COMMAND_INDEX.commands.values():
    function = command.command.call
    app.command(
        f"{command.name}",
        help=command.command.description,
    )(function)


if __name__ == "__main__":
    app()
