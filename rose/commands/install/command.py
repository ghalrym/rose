from rose.command_framework.command import Command
from rose.command_framework.command_index import CommandIndex


class InstallCommand(Command):
    def __init__(self):
        super().__init__(
            name="install",
            description="Install a command from GET",
        )

    @staticmethod
    def call(install_url: str) -> None:
        """Install a command from the store"""
        command_index = CommandIndex()
        command_index.install_command(install_url)
