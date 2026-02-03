# Environment Variables

Manage environment variables: list names, check existence, load from a `.env` file, or unset a variable.

## How to run

All invocations use:

```bash
rose run environment_variables <subcommand> [args...]
```

## Subcommands

### `list`

Print the names of all current environment variables (one per line).

**Usage:**

```bash
rose run environment_variables list
```

**Args:** none.

---

### `exists <name>`

Check whether an environment variable is set. Prints `Variable <name> exists` or `Variable <name> does not exist`.

**Usage:**

```bash
rose run environment_variables exists MY_VAR
```

**Args:** `args[0]` = `"exists"`, `args[1]` = variable name.

---

### `load-from-env-file [path]`

Load variables from an env file into the current process environment. Each line should be `KEY=VALUE`. Default file is `.env` if no path is given.

**Usage:**

```bash
rose run environment_variables load-from-env-file
rose run environment_variables load-from-env-file .env.local
```

**Args:** `args[0]` = `"load-from-env-file"`, `args[1]` = optional path (default `".env"`).

---

### `unset <name>`

Remove an environment variable from the current process. Prints `Variable <name> has been removed`. Requires the variable name.

**Usage:**

```bash
rose run environment_variables unset MY_VAR
```

**Args:** `args[0]` = `"unset"`, `args[1]` = variable name. Raises `ValueError("Missing variable name")` if `args[1]` is missing.
