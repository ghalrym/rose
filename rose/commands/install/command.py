import typer

from rose.command_framework.command import Command
from rose.command_framework.command_index import CommandIndex


class InstallCommand(Command):
    def __init__(self):
        super().__init__(
            name="install",
            description="Install a command from GET",
        )

    @staticmethod
    def call(
        install_url: str = typer.Argument(
            ..., help="The URL of the command to install"
        ),
    ) -> None:
        """Install a command from the store"""
        command_index = CommandIndex()
        command_index.install_command(install_url)
