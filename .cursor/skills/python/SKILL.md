---
name: python-styling
description: Enforces Python code style: Ruff formatting, global imports only, OOP preference, reusable code and fewer code pathways, Pydantic typing, full type annotations, and structured docstrings. Use when writing or editing Python code, reviewing Python files, or when the user mentions Python style, ruff, pydantic, or typing. When the user gives feedback on code or states preferences, update the style docs and design patterns so future code follows them.
---

# Python

Apply these rules whenever writing or editing Python in this project.

## Style rules (by topic)

| Topic | Rules |
|-------|--------|
| **Formatting** | Ruff only; respect `ruff.toml` / `pyproject.toml`. See [style/formatting.md](style/formatting.md). |
| **Naming** | Full words, no abbreviations, no single-letter names. See [style/naming.md](style/naming.md). |
| **Imports** | Module top level only; stdlib → third-party → first-party, alphabetized. See [style/imports.md](style/imports.md). |
| **Architecture** | OOP by default; only CLI/route handler is a thin plain function; FastAPI dependencies in a dedicated module. See [style/architecture.md](style/architecture.md). |
| **Circular imports** | Resolve with single-responsibility modules and splitting, not lazy imports or validators. See [style/circular-imports.md](style/circular-imports.md). |
| **Reusable code** | Behavior on natural owner; fewer branches; refactor instead of edge-case handling. See [style/reusable-code.md](style/reusable-code.md). |
| **Typing** | Pydantic for structured/validated data; full annotations; conversions and factories as methods on the source/created type. See [style/typing.md](style/typing.md). |
| **Docstrings** | Definition, Args, Returns, Raises for public API. See [style/docstrings.md](style/docstrings.md). |

## Design patterns

When structuring code (creation, composition, or interaction), use the pattern docs for when to use each, structure, and Python examples. Full index: [design-patterns/README.md](design-patterns/README.md).

| Category | Patterns |
|----------|----------|
| **Creational** | [Singleton](design-patterns/creational/singleton.md), [Factory Method](design-patterns/creational/factory-method.md), [Abstract Factory](design-patterns/creational/abstract-factory.md), [Builder](design-patterns/creational/builder.md), [Prototype](design-patterns/creational/prototype.md) |
| **Structural** | [Adapter](design-patterns/structural/adapter.md), [Bridge](design-patterns/structural/bridge.md), [Composite](design-patterns/structural/composite.md), [Decorator](design-patterns/structural/decorator.md), [Facade](design-patterns/structural/facade.md), [Flyweight](design-patterns/structural/flyweight.md), [Proxy](design-patterns/structural/proxy.md) |
| **Behavioral** | [Chain of Responsibility](design-patterns/behavioral/chain-of-responsibility.md), [Command](design-patterns/behavioral/command.md), [Iterator](design-patterns/behavioral/iterator.md), [Mediator](design-patterns/behavioral/mediator.md), [Memento](design-patterns/behavioral/memento.md), [Observer](design-patterns/behavioral/observer.md), [State](design-patterns/behavioral/state.md), [Strategy](design-patterns/behavioral/strategy.md), [Template Method](design-patterns/behavioral/template-method.md), [Visitor](design-patterns/behavioral/visitor.md) |

## Updating rules from feedback

When the user gives **feedback on code** or states **preferences** (e.g. "I prefer X", "don't do Y", "we always do Z"), update the skill so future code follows them:

1. **Identify what to update**
   - Style/preference (naming, formatting, imports, architecture, typing, docstrings, etc.) → update the matching file in [style/](style/) (e.g. [style/naming.md](style/naming.md), [style/architecture.md](style/architecture.md)).
   - Structure, patterns, or how to implement something → update [design-patterns/README.md](design-patterns/README.md) or the relevant pattern file under [design-patterns/](design-patterns/) (creational, structural, behavioral).

2. **Edit the documents**
   - Open the relevant style or design-pattern file and add, change, or clarify rules so they reflect the user's preference. Keep the same format and level of detail as the rest of the file.

3. **Confirm**
   - Briefly say what you updated (e.g. "Updated style/naming.md to prefer …") so the user sees the change is persisted.

Do not skip this step: feedback on code is an instruction to update the rules, not only to fix the current snippet.

## Quick checklist

- [ ] Ruff-compliant formatting; config respected if present
- [ ] Naming: full words, no abbreviations, no single-letter names (e.g. no `a`, `x`, `i`, `e`)
- [ ] Imports only at module top level
- [ ] Logic in classes; only the CLI/route handler is a thin plain function that delegates (e.g. `Installer().run()`)
- [ ] No circular imports; resolve with single-responsibility modules and splitting, not lazy imports or validators
- [ ] Reusable code: behavior on natural owner; fewer branches; refactor instead of edge cases; delete dead code (no stubs or unused modules left behind)
- [ ] Pydantic for structured/validated data
- [ ] Conversions between types implemented as methods on the source ("from") class
- [ ] All parameters and return values typed
- [ ] Docstrings: definition, Args, Returns, Raises (where applicable)
