import os
import shutil
from rose.command_framework.command import Command
from rose.command_framework.command_index import CommandIndex


class CreateCommandCommand(Command):
    def __init__(self):
        super().__init__(
            name="create_command",
            description="Create a new command from a template",
        )

    @staticmethod
    def call(args: list[str]) -> None:
        if len(args) != 1:
            raise ValueError("Missing command name")
        # Get command name
        command_name = args[0]

        # for file in template directory copy to commands directory
        template_directory = os.path.join(os.path.dirname(__file__), "template")
        # Create commands directory if it doesn't exist
        if not os.path.exists(os.path.join(os.path.dirname(__file__), "..", "..", "commands", command_name)):
            os.makedirs(os.path.join(os.path.dirname(__file__), "..", "..", "commands", command_name))
        commands_directory = os.path.join(os.path.dirname(__file__), "..", "..", "commands", command_name)
        for file in os.listdir(template_directory):
            shutil.copy(os.path.join(template_directory, file), os.path.join(commands_directory, file))
            # Find and replace *NAME* with command name
            with open(os.path.join(commands_directory, file), "r") as f:
                content = f.read()
            content = content.replace("*NAME*", command_name.replace(" ", "_").lower())
            content = content.replace("*PascalCaseName*", command_name.replace(" ", "").capitalize())
            with open(os.path.join(commands_directory, file), "w") as f:
                f.write(content)

        # Add command to command index
        command_index = CommandIndex()
        command_index.add_command(Command(command_name, "TODO: Add description"))
        command_index.save()