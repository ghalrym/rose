# Rose CLI

A home for assistant commands. Run `rose` from any directory after installing.

## Install

**Prerequisites:** Python 3.8+ and pip.

1. Clone the repo and go to the project root:

```bash
cd path/to/Rose
```

2. Install the package (editable so you can change the code and run it):

```bash
pip install -e .
```

3. Run `rose` from any directory:

```bash
rose
rose version
```

To install a fixed copy (not editable), use `pip install .` instead of `pip install -e .`.

## Usage

- List commands and help: **`rose`**
- Show version: **`rose version`**
- Install a command from the store: **`rose install GIT_URL`**
- Read a command’s skill doc: **`rose skill COMMAND_NAME`**

See **`rose`** and **`rose skill <command>`** for full usage and command-specific docs.
