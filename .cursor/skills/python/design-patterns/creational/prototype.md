# Prototype

Create new objects by **copying an existing object (prototype)** instead of constructing from scratch.

## When to use

- Creating a new instance is more expensive or complex than copying (e.g. heavy initialization, many dependencies).
- You want to avoid a deep class hierarchy just to get different initial states—clone and then modify.
- Initial state is determined at runtime (e.g. from config or previous object).

## Structure

- **Prototype**: Interface (or base class) that supports cloning itself. In Python, that’s often `copy.copy()` or `copy.deepcopy()` plus a custom `clone()` method if needed.
- **ConcretePrototype**: Implements cloning; may customize what gets copied (shallow vs deep).

## Python example: shallow vs deep copy

```python
import copy
from dataclasses import dataclass
from typing import Any

@dataclass
class Document:
    title: str
    content: list[str]
    metadata: dict[str, Any]

    def clone(self, deep: bool = True) -> "Document":
        if deep:
            return copy.deepcopy(self)
        return copy.copy(self)

# Usage
original = Document("Report", ["Section 1", "Section 2"], {"author": "Alice"})
shallow = original.clone(deep=False)
deep = original.clone(deep=True)

original.content.append("Section 3")
print(shallow.content)  # ['Section 1', 'Section 2', 'Section 3'] — shared list
print(deep.content)     # ['Section 1', 'Section 2'] — independent copy
```

## Python example: prototype registry

Keep a set of preconfigured prototypes and clone the right one when needed:

```python
from copy import deepcopy
from typing import Any

class CellConfig:
    """Prototype for a spreadsheet cell configuration."""
    def __init__(
        self,
        font: str = "Arial",
        font_size: int = 12,
        bold: bool = False,
        formula: str | None = None,
    ):
        self.font = font
        self.font_size = font_size
        self.bold = bold
        self.formula = formula

    def clone(self, **overrides: Any) -> "CellConfig":
        copy = deepcopy(self)
        for key, value in overrides.items():
            setattr(copy, key, value)
        return copy


class CellConfigRegistry:
    """Registry of named prototypes."""
    def __init__(self):
        self._prototypes: dict[str, CellConfig] = {}

    def register(self, name: str, config: CellConfig) -> None:
        self._prototypes[name] = config

    def create(self, name: str, **overrides: Any) -> CellConfig:
        if name not in self._prototypes:
            raise KeyError(f"Unknown config: {name}")
        return self._prototypes[name].clone(**overrides)


# Usage
registry = CellConfigRegistry()
registry.register("default", CellConfig())
registry.register("header", CellConfig(font_size=14, bold=True))
registry.register("formula", CellConfig(formula="=SUM(A1:A10)"))

cell1 = registry.create("header")                    # clone header prototype
cell2 = registry.create("formula", font_size=10)    # clone formula, override size
```

## Python example: game entity from prototype

```python
from dataclasses import dataclass
from copy import deepcopy

@dataclass
class Enemy:
    name: str
    health: int
    damage: int
    speed: float

    def clone(self) -> "Enemy":
        return deepcopy(self)

# Predefined prototypes
GOBLIN = Enemy("Goblin", health=30, damage=5, speed=1.2)
ORC = Enemy("Orc", health=80, damage=15, speed=0.8)

# Spawn multiple enemies from same prototype without re-specifying attributes
enemies = [GOBLIN.clone() for _ in range(5)]
enemies[0].name = "Goblin Chief"  # customize one
enemies[0].health = 50
```

## When to use `copy.copy` vs `copy.deepcopy`

- **Shallow**: New object, but nested objects (lists, dicts, other refs) are shared. Use when nested state is immutable or you want to share it.
- **Deep**: Recursive copy; nested structures are copied too. Use when the object has mutable nested state that must be independent.

For true “clone and tweak” behavior, `deepcopy` is usually what you want unless you explicitly need shared internals.

## Summary

| Pros | Cons |
|------|------|
| Avoid repeated complex initialization | Cloning can be tricky (circular refs, deep copy cost) |
| Add new “kinds” without new classes | |
| Runtime configuration via prototype state | |

Use Prototype when **copying is cheaper or simpler than building from scratch**, or when you have **preconfigured templates** to clone.
