import os
from rose.command_framework.command import Command


class EnvironmentVariablesCommand(Command):
    def __init__(self):
        super().__init__(
            name="environment_variables",
            description="Manage environment variables",
        )

    @staticmethod
    def call(args: list[str]) -> None:
        if len(args) < 1:
            raise ValueError("No command provided")
        elif len(args) > 2:
            raise ValueError("Too many arguments provided")
        
        command = args[0]
        if command == "list":
            for key, value in os.environ.items():
                print(f"{key}")
        elif command == "exists":
            if key in os.environ:
                print(f"Variable {key} exists")
            else:
                print(f"Variable {key} does not exist")
        elif command == "load-from-env-file":
            env_file = args[1] if len(args) > 1 else ".env"
            with open(env_file, "r") as file:
                for line in file:
                    key, value = line.strip().split("=")
                    os.environ[key] = value
        elif command == "unset":
            if len(args) != 2:
                raise ValueError("Missing variable name")
            key = args[1]
            if key in os.environ:
                del os.environ[key]
            print(f"Variable {key} has been removed")
