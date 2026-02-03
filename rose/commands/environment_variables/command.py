import os

import typer

from rose.command_framework.command import Command


class EnvironmentVariablesCommand(Command):
    def __init__(self):
        super().__init__(
            name="environment_variables",
            description="Manage environment variables",
        )

    @staticmethod
    def call(
        command: str = typer.Argument(
            help="The command to run (list, exists, load-from-env-file, unset)"
        ),
        dot_env_file_loc: str | None = typer.Option(
            None,
            "--dot-env-file-loc",
            "-d",
            help="The location of the .env file to manage",
        ),
        variable_name: str | None = typer.Option(
            None,
            "--variable-name",
            "-v",
            help="The name of the environment variable to manage",
        ),
    ) -> None:
        if command == "list":
            for key, value in os.environ.items():
                print(f"{key}")
        elif command == "exists":
            if key in os.environ:
                print(f"Variable {key} exists")
            else:
                print(f"Variable {key} does not exist")
        elif command == "load-from-env-file":
            env_file = dot_env_file_loc or ".env"
            with open(env_file, "r") as file:
                for line in file:
                    key, value = line.strip().split("=")
                    os.environ[key] = value
        elif command == "unset":
            if variable_name is None:
                raise typer.BadParameter("Missing variable name")
            if variable_name in os.environ:
                del os.environ[variable_name]
            print(f"Variable {variable_name} has been removed")
        else:
            typer.echo(f"Invalid command: {command}")
            typer.echo("Available commands: list, exists, load-from-env-file, unset")
