# Flyweight

Use **sharing** to support large numbers of fine-grained objects efficiently. Flyweight separates **intrinsic state** (shared, immutable) from **extrinsic state** (passed in when needed).

## When to use

- Your application uses a huge number of objects and memory/creation cost is high.
- Most of each object’s state can be made extrinsic (same for many instances).
- You can replace many duplicate objects with a smaller set of shared flyweights plus extrinsic state (e.g. position, color at draw time).

## Structure

- **Flyweight**: Stores intrinsic (shared) state; accepts extrinsic state as arguments to methods.
- **FlyweightFactory**: Creates and manages flyweights; returns existing one when appropriate (e.g. keyed by intrinsic state).
- **Client**: Holds or computes extrinsic state and passes it when using the flyweight.

## Python example: character flyweight (text editor)

Many characters share the same font/size; only position and maybe color differ per occurrence.

```python
from dataclasses import dataclass

# --- Flyweight: intrinsic state only ---
@dataclass(frozen=True)
class CharacterStyle:
    """Intrinsic: shared by many characters."""
    font: str
    size: int
    bold: bool

class CharacterFlyweight:
    """Shared character rendering info; extrinsic state passed at render time."""
    def __init__(self, char: str, style: CharacterStyle):
        self.char = char
        self.style = style

    def render(self, x: int, y: int, color: str) -> str:
        """Extrinsic state (x, y, color) passed in."""
        return f"'{self.char}' at ({x},{y}) {self.style.font} {self.style.size}pt color={color}"


# --- Factory: reuse flyweights by (char, style) ---
class CharacterFactory:
    def __init__(self):
        self._cache: dict[tuple[str, CharacterStyle], CharacterFlyweight] = {}

    def get_character(self, char: str, style: CharacterStyle) -> CharacterFlyweight:
        key = (char, style)
        if key not in self._cache:
            self._cache[key] = CharacterFlyweight(char, style)
        return self._cache[key]


# --- Client: holds extrinsic state (position), uses flyweight ---
class Glyph:
    def __init__(self, flyweight: CharacterFlyweight, x: int, y: int, color: str):
        self.flyweight = flyweight
        self.x, self.y, self.color = x, y, color

    def render(self) -> str:
        return self.flyweight.render(self.x, self.y, self.color)


# Usage
factory = CharacterFactory()
style = CharacterStyle("Arial", 12, False)
a1 = factory.get_character("a", style)
a2 = factory.get_character("a", style)
assert a1 is a2  # same flyweight

glyphs = [
    Glyph(factory.get_character("H", style), 0, 0, "black"),
    Glyph(factory.get_character("i", style), 10, 0, "black"),
]
for g in glyphs:
    print(g.render())
```

## Python example: tree type in a game

Many trees share mesh/texture; only position and scale vary per instance.

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class TreeType:
    """Intrinsic: name, mesh_id, texture_id — shared by many trees."""
    name: str
    mesh_id: str
    texture_id: str

class Tree:
    """Flyweight: shared type + render with extrinsic state."""
    def __init__(self, tree_type: TreeType):
        self.tree_type = tree_type

    def draw(self, x: float, y: float, scale: float) -> str:
        return f"Drawing {self.tree_type.name} at ({x},{y}) scale={scale}"

class TreeFactory:
    _pool: dict[str, Tree] = {}

    @classmethod
    def get_tree(cls, name: str, mesh_id: str, texture_id: str) -> Tree:
        key = (name, mesh_id, texture_id)
        if key not in cls._pool:
            cls._pool[key] = Tree(TreeType(name, mesh_id, texture_id))
        return cls._pool[key]

# 1000 trees, only 2 Tree instances (oak and pine)
oak = TreeFactory.get_tree("Oak", "mesh_1", "tex_bark")
pine = TreeFactory.get_tree("Pine", "mesh_2", "tex_pine")
for i in range(500):
    tree = TreeFactory.get_tree("Oak", "mesh_1", "tex_bark")
    tree.draw(i * 1.0, 0, 1.0)
```

## When Flyweight helps

- **Intrinsic state** is the same for many logical “objects” (e.g. character + font, tree type).
- **Extrinsic state** is what varies per occurrence (position, color, scale) and can be passed in when needed.
- You **cache** flyweights by intrinsic state so you don’t create duplicates.

## Summary

| Pros | Cons |
|------|------|
| Large memory savings when many objects share state | More complex: separate intrinsic/extrinsic, factory |
| Fewer allocations | |
| | Only works when state clearly splits shared vs per-instance |

Use Flyweight when you have **many objects** that share a **large part of their state** and you can pass the rest (extrinsic) at use time.
