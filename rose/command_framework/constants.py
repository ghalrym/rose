import re
from pathlib import Path

VERSION = "0.1.0"
PROJECT_DIR = Path(__file__).parent.parent
REQUIREMENTS_FILE = PROJECT_DIR / "requirements.txt"
COMMANDS_INDEX_FILE = PROJECT_DIR / "commands.index"
COMMANDS_DIR = "commands"
SAVED_VARIABLES_FILE = PROJECT_DIR / "variables.json"

REQUIREMENT_REGEX = re.compile(
    r"^(?P<package>[^><=]+)(?P<version_operator>([^><=]+))(?P<version>[^,]+)(?:,(?P<max_version_operator>([<>=]+))?(?P<max_version>[^,]+))?$",
)
