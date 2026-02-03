import importlib
from types import ModuleType
from typing import TYPE_CHECKING, Any, NamedTuple

if TYPE_CHECKING:
    from .command import Command


class CommandArgument(NamedTuple):
    name: str
    description: str
    required: bool
    type: str
    default: Any | None = None


class CommandIndexEntry(NamedTuple):
    name: str

    @property
    def module(self) -> ModuleType:
        return importlib.import_module(f"rose.commands.{self.name}")

    @property
    def command(self) -> "Command":
        return self.module.Command()


class PythonRequirement(NamedTuple):
    package: str
    version_operator: str
    version: str
    max_version_operator: str = None
    max_version: str | None = None

    def is_met(self, current_requirement: "PythonRequirement") -> bool:
        if self.version_operator == "=":
            return self.version >= current_requirement.version
        elif self.version_operator == ">":
            return self.version > current_requirement.version
        elif self.version_operator == "<":
            return self.version < current_requirement.version
        elif self.version_operator == ">=":
            return self.version >= current_requirement.version
        elif self.version_operator == "<=":
            return self.version <= current_requirement.version
        else:
            raise ValueError(f"Unknown version operator: {self.version_operator}")
