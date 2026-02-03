import json
import subprocess
from typing import Any

from rose.command_framework.constants import (
    COMMANDS_DIR,
    PROJECT_DIR,
    REQUIREMENT_REGEX,
    REQUIREMENTS_FILE,
    SAVED_VARIABLES_FILE,
)
from rose.command_framework.types import CommandArgument, PythonRequirement


class Command:
    def __init__(
        self,
        name: str,
        description: str,
        requirements: set[PythonRequirement] | None = None,
        arguments: list[CommandArgument] | None = None,
    ):
        self.name = name
        self.requirements = requirements or set()
        self.arguments = arguments or []
        self.description = description

        # Run Validation
        for requirement in self.requirements:
            if requirement.max_version_operator:
                raise NotImplementedError("Max version operator is not supported yet")

        # Check for SKILLS.md file
        skill_file = PROJECT_DIR / COMMANDS_DIR / f"{self.name}" / "SKILL.md"
        if not skill_file.exists():
            raise ValueError(f"SKILL.md file not found for command {self.name}")

        # Read the SKILLS.md file
        with open(skill_file, "r") as f:
            self.skill_markdown = f.read()

    def install(self) -> None:
        # Retrieve Current Requirements
        current_requirements = {}
        with open(REQUIREMENTS_FILE, "r") as f:
            for line in f:
                match = REQUIREMENT_REGEX.match(line)
                if match:
                    package_name = match.group("package").strip()
                    current_requirements[package_name] = PythonRequirement(
                        package=package_name,
                        version_operator=match.group("version_operator").strip(),
                        version=match.group("version").strip(),
                        max_version_operator=match.group(
                            "max_version_operator"
                        ).strip(),
                        max_version=match.group("max_version").strip(),
                    )

        # Check if any requiremes clash
        new_requirements = {}
        for requirement in self.requirements:
            if requirement.package in current_requirements:
                if requirement.is_met(current_requirements[requirement.package]):
                    new_requirements[requirement.package] = requirement
                else:
                    raise ValueError(
                        f"Requirement {requirement.package} already exists in requirements.txt but does not meet the new requirement"
                    )

        # Write the requirements to the file
        with open(REQUIREMENTS_FILE, "w") as f:
            for requirement in new_requirements:
                f.write(
                    f"{requirement.package}{requirement.version_operator}{requirement.version}"
                )
                if requirement.max_version_operator and requirement.max_version:
                    f.write(
                        f",{requirement.max_version_operator}{requirement.max_version}"
                    )
                f.write("\n")

        # Install the requirements
        result = subprocess.run(["pip", "install", "-r", REQUIREMENTS_FILE])
        if result.returncode != 0:
            # revert the requirements file
            with open(REQUIREMENTS_FILE, "w") as f:
                for requirement in current_requirements:
                    f.write(
                        f"{requirement.package}{requirement.version_operator}{requirement.version}"
                    )
                    if requirement.max_version_operator and requirement.max_version:
                        f.write(
                            f",{requirement.max_version_operator}{requirement.max_version}"
                        )
                    f.write("\n")
            raise RuntimeError(f"Failed to install requirements: {result.stderr}")

    @staticmethod
    def call(args: list[str]) -> None:
        raise NotImplementedError("This command does not have a call method")

    def get_variable(self, variable: Any, command: None | str = None) -> Any:
        with open(SAVED_VARIABLES_FILE, "r") as f:
            return json.load(f).get(command or self.name, {}).get(variable, None)

    def set_variable(
        self, variable: Any, value: Any, command: None | str = None
    ) -> None:
        with open(SAVED_VARIABLES_FILE, "r") as f:
            variables = json.load(f)
        variables[command or self.name][variable] = value
        with open(SAVED_VARIABLES_FILE, "w") as f:
            json.dump(variables, f)
