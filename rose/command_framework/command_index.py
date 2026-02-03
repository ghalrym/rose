import subprocess
from functools import lru_cache
from typing import Any

from rose.command_framework.command import Command
from rose.command_framework.constants import COMMANDS_INDEX_FILE, VERSION
from rose.command_framework.types import CommandIndexEntry


class CommandIndex:
    commands: dict[str, CommandIndexEntry] = {}

    def __init__(self):
        self.load()

    @staticmethod
    @lru_cache(maxsize=1)
    def load() -> None:
        for line in COMMANDS_INDEX_FILE.read_text().splitlines():
            name = line.strip()
            CommandIndex.commands[name] = CommandIndexEntry(name)

    def add_command(self, command: Command) -> None:
        self.commands[command.name] = CommandIndexEntry(command.name)

    def remove_command(self, name: str) -> None:
        if name not in self.commands:
            raise ValueError(f"Command {name} not found")
        del self.commands[name]

    def load_command(self, name: str) -> Command:
        if name not in self.commands:
            raise ValueError(f"Command {name} not found")
        return self.commands[name].command

    def generate_schema(self) -> dict[str, Any]:
        """Generate the schema for the command"""
        return {
            "version": VERSION,
            "commands": [
                {
                    "name": command.name,
                    "skill": command.skill_markdown,
                    "arguments": [
                        {
                            "name": argument.name,
                            "description": argument.description,
                            "required": argument.required,
                            "type": argument.type,
                            "default": argument.default,
                        }
                        for argument in command.arguments
                    ],
                }
                for command in self.commands
            ],
        }

    def save(self) -> None:
        with open(COMMANDS_INDEX_FILE, "w") as f:
            for name in self.commands:
                f.write(f"{name}\n")

    def install_command(self, install_url: str) -> None:
        # CLONE package from GIT
        subprocess.run(["cd", "commands", "&&", "git", "clone", install_url])

        # Load the command entry
        command_entry = CommandIndexEntry(install_url)
        command_entry.command.install()
        self.add_command(command_entry.command)
        self.save()

    def uninstall_command(self, name: str) -> None:
        # Load the command entry
        command_entry = CommandIndexEntry(name)
        command_entry.command.uninstall()
        self.remove_command(name)
        self.save()

        # TODO: DELETE package
