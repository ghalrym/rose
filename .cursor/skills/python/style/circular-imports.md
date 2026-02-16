# Circular Imports

- **Prefer structure over workarounds**: When you see a circular import, do not fix it with lazy imports (e.g. importing inside a function or validator), `TYPE_CHECKING`-only imports, or `BeforeValidator`-style coercion just to defer an import. Those hide the design problem.
- **Single responsibility**: Give each module one clear responsibility so dependency direction is obvious and cycles do not form. For example: a module that only defines an enum and model choices (e.g. `Provider`) should not also build runtime objects that depend on config (e.g. LangChain models from `AgentConfig`). Move the builder to its own module that imports both the enum and the config.
- **Break cycles by splitting**: If A imports B and B imports A, extract one direction into a new module (e.g. move the heavy or config-dependent logic out of the enum/types module). Then A and B both depend on the new module and the cycle is gone.
