# Composite

Compose objects into **tree structures** to represent part-whole hierarchies. Clients treat individual objects and compositions of objects uniformly.

## When to use

- You have a tree of objects (e.g. file system, UI widget tree, document sections) and want to apply the same operations to leaves and branches.
- You want clients to ignore the difference between a single object and a group; both support the same interface (e.g. `render()`, `get_size()`).

## Structure

- **Component**: Abstract interface for both leaves and composites (e.g. `draw()`, `get_size()`).
- **Leaf**: Represents a single object; implements Component, no children.
- **Composite**: Holds a collection of child Components; implements Component by delegating to children (and often adding/removing children).

## Python example: file system (files and folders)

```python
from abc import ABC, abstractmethod

class FileSystemNode(ABC):
    """Component: common interface for files and folders."""
    @abstractmethod
    def size(self) -> int:
        pass

    @abstractmethod
    def name(self) -> str:
        pass

class File(FileSystemNode):
    """Leaf."""
    def __init__(self, name: str, size_bytes: int):
        self._name = name
        self._size = size_bytes

    def name(self) -> str:
        return self._name

    def size(self) -> int:
        return self._size

class Folder(FileSystemNode):
    """Composite: contains children."""
    def __init__(self, name: str):
        self._name = name
        self._children: list[FileSystemNode] = []

    def name(self) -> str:
        return self._name

    def size(self) -> int:
        return sum(child.size() for child in self._children)

    def add(self, node: FileSystemNode) -> None:
        self._children.append(node)

    def remove(self, node: FileSystemNode) -> None:
        self._children.remove(node)

    def __iter__(self):
        return iter(self._children)


# Usage
root = Folder("root")
root.add(File("a.txt", 100))
root.add(File("b.txt", 200))
sub = Folder("sub")
sub.add(File("c.txt", 50))
root.add(sub)

print(root.size())  # 350 — same interface for file and folder
```

## Python example: UI widget tree

```python
from abc import ABC, abstractmethod

class Widget(ABC):
    @abstractmethod
    def render(self) -> str:
        pass

    @abstractmethod
    def get_rect(self) -> tuple[int, int, int, int]:  # x, y, w, h
        pass

class Button(Widget):
    """Leaf."""
    def __init__(self, label: str, x: int, y: int, w: int, h: int):
        self.label = label
        self.rect = (x, y, w, h)

    def render(self) -> str:
        return f"<button>{self.label}</button>"

    def get_rect(self) -> tuple[int, int, int, int]:
        return self.rect

class Panel(Widget):
    """Composite."""
    def __init__(self, x: int, y: int, w: int, h: int):
        self.rect = (x, y, w, h)
        self.children: list[Widget] = []

    def add(self, widget: Widget) -> None:
        self.children.append(widget)

    def render(self) -> str:
        parts = [f"<panel>"] + [c.render() for c in self.children] + ["</panel>"]
        return "".join(parts)

    def get_rect(self) -> tuple[int, int, int, int]:
        return self.rect

# Client treats leaf and composite the same
def paint(widget: Widget) -> None:
    print(widget.render())

button = Button("OK", 0, 0, 80, 24)
panel = Panel(0, 0, 200, 100)
panel.add(Button("Cancel", 10, 10, 80, 24))
panel.add(Button("Save", 100, 10, 80, 24))
paint(button)
paint(panel)
```

## Traversing the tree

You can add methods that work over the whole tree (e.g. find by name, collect all leaves):

```python
class FileSystemNode(ABC):
    # ... as before ...
    def find(self, name: str) -> "FileSystemNode | None":
        if self.name() == name:
            return self
        if isinstance(self, Folder):
            for child in self:
                found = child.find(name)
                if found:
                    return found
        return None
```

## Summary

| Pros | Cons |
|------|------|
| Uniform handling of single and composite objects | Can make the design too general; leaves might not need all operations |
| Easy to add new component types | |
| Tree structure matches problem domain | |

Use Composite when you have a **part-whole hierarchy** and want to **treat leaves and groups the same** (same interface, recursive operations).
