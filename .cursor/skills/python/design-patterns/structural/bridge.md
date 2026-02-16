# Bridge

Decouple an **abstraction** from its **implementation** so the two can vary independently. Use composition to hold the implementation instead of binding it with inheritance.

## When to use

- You want to avoid a permanent binding between an abstraction and one of many possible implementations (e.g. different window systems, storage backends).
- Both abstractions and implementations should be extensible by subclassing; Bridge lets you combine them without a combinatorial explosion of subclasses.
- You want to switch implementations at runtime.

## Structure

- **Abstraction**: High-level interface used by the client; holds a reference to an **Implementor**.
- **RefinedAbstraction**: Extends the abstraction (optional).
- **Implementor**: Interface for implementation (e.g. “how to draw”).
- **ConcreteImplementor**: Actual implementation (e.g. “draw on Windows”, “draw on Linux”).

## Python example: renderer abstraction

Different shapes (abstraction) can be drawn with different renderers (implementation):

```python
from abc import ABC, abstractmethod

# --- Implementor ---
class Renderer(ABC):
    @abstractmethod
    def draw_circle(self, x: float, y: float, radius: float) -> str:
        pass

    @abstractmethod
    def draw_rect(self, x: float, y: float, w: float, h: float) -> str:
        pass

class VectorRenderer(Renderer):
    def draw_circle(self, x: float, y: float, radius: float) -> str:
        return f"Vector circle at ({x},{y}) r={radius}"

    def draw_rect(self, x: float, y: float, w: float, h: float) -> str:
        return f"Vector rect at ({x},{y}) {w}x{h}"

class RasterRenderer(Renderer):
    def draw_circle(self, x: float, y: float, radius: float) -> str:
        return f"Pixel circle at ({x},{y}) r={radius}"

    def draw_rect(self, x: float, y: float, w: float, h: float) -> str:
        return f"Pixel rect at ({x},{y}) {w}x{h}"


# --- Abstraction: holds a Renderer ---
class Shape(ABC):
    def __init__(self, renderer: Renderer):
        self.renderer = renderer

    @abstractmethod
    def draw(self) -> str:
        pass

class Circle(Shape):
    def __init__(self, renderer: Renderer, x: float, y: float, radius: float):
        super().__init__(renderer)
        self.x, self.y, self.radius = x, y, radius

    def draw(self) -> str:
        return self.renderer.draw_circle(self.x, self.y, self.radius)

class Rectangle(Shape):
    def __init__(self, renderer: Renderer, x: float, y: float, w: float, h: float):
        super().__init__(renderer)
        self.x, self.y, self.w, self.h = x, y, w, h

    def draw(self) -> str:
        return self.renderer.draw_rect(self.x, self.y, self.w, self.h)


# Usage: mix any shape with any renderer
circle_vector = Circle(VectorRenderer(), 10, 10, 5)
circle_raster = Circle(RasterRenderer(), 10, 10, 5)
print(circle_vector.draw())  # Vector circle at (10,10) r=5
print(circle_raster.draw()) # Pixel circle at (10,10) r=5
```

## Python example: storage abstraction

Abstraction = “repository”; implementation = “how/where data is stored”:

```python
from abc import ABC, abstractmethod

# --- Implementor ---
class StorageBackend(ABC):
    @abstractmethod
    def read(self, key: str) -> bytes | None:
        pass

    @abstractmethod
    def write(self, key: str, data: bytes) -> None:
        pass

class FileStorage(StorageBackend):
    def __init__(self, root: str):
        self.root = root
    def read(self, key: str) -> bytes | None:
        path = f"{self.root}/{key}"
        try:
            return open(path, "rb").read()
        except FileNotFoundError:
            return None
    def write(self, key: str, data: bytes) -> None:
        path = f"{self.root}/{key}"
        open(path, "wb").write(data)

class MemoryStorage(StorageBackend):
    def __init__(self):
        self._data: dict[str, bytes] = {}
    def read(self, key: str) -> bytes | None:
        return self._data.get(key)
    def write(self, key: str, data: bytes) -> None:
        self._data[key] = data

# --- Abstraction ---
class KeyValueStore:
    def __init__(self, backend: StorageBackend):
        self._backend = backend

    def get(self, key: str) -> str | None:
        raw = self._backend.read(key)
        return raw.decode("utf-8") if raw else None

    def set(self, key: str, value: str) -> None:
        self._backend.write(key, value.encode("utf-8"))

# Usage: same abstraction, different backends
store = KeyValueStore(MemoryStorage())
store.set("name", "Alice")
print(store.get("name"))
```

## Bridge vs Adapter

- **Adapter**: One existing interface doesn’t match another; adapter translates. You’re adapting a specific adaptee to a target.
- **Bridge**: You design abstraction and implementation separately and connect them. Both sides are under your control (or you’re defining the split up front).

## Summary

| Pros | Cons |
|------|------|
| Abstraction and implementation vary independently | More classes (abstraction + implementor hierarchies) |
| Avoids explosion of subclasses | |
| Can swap implementation at runtime | |

Use Bridge when you have **multiple dimensions of variation** (e.g. shape × renderer, repository × storage) and want to **compose** them instead of subclassing every combination.
