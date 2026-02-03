# Create Command

Use this skill when adding a new Rose CLI command to the project.

## Steps

### 1. Run the command to create a new project

From the project root, run:

```bash
python -m rose run create_command <command_name>
```

Replace `<command_name>` with the name of your command (e.g. `my_tool` or `do_thing`). This creates a new command directory under `rose/commands/<command_name>/` and copies the template files, substituting the command name and PascalCase class name where needed.

### 2. Edit the run method of the command

Open `rose/commands/<command_name>/command.py` and implement the **`call`** method. This is the method that runs when the command is executed. It receives `args: list[str]` (the arguments passed after the command name). Replace the `# TODO: Implement command logic` placeholder with your command’s behavior.

Example:

```python
def call(self, args: list[str]) -> None:
    if not args:
        raise ValueError("Expected at least one argument")
    # Your logic here
    ...
```

After implementing `call`, your new command is available via:

```bash
python -m rose run <command_name> [args...]
```
