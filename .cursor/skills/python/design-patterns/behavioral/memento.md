# Memento

**Capture and externalize an object’s internal state** so the object can be restored to that state later, without exposing its internals.

## When to use

- You need to implement **undo** (restore previous state) or **checkpoints** (save/load).
- You don’t want to expose the full state of the object for encapsulation reasons; the memento holds a snapshot that only the originator can interpret.

## Structure

- **Originator**: The object whose state is saved. Creates a **Memento** with a snapshot of its state and can restore from a Memento.
- **Memento**: Opaque object that stores the originator’s state. Only the originator can read/write it (or a narrow interface is exposed).
- **Caretaker**: Holds mementos (e.g. undo stack) and asks the originator to restore when needed. It doesn’t interpret the memento’s contents.

## Python example: text editor undo

```python
from dataclasses import dataclass
from typing import Any

class Memento:
    """Stores state; only originator should know the structure."""
    def __init__(self, state: dict[str, Any]):
        self._state = state.copy()

    def get_state(self) -> dict[str, Any]:
        return self._state.copy()

class TextEditor:
    """Originator."""
    def __init__(self):
        self._text = ""
        self._cursor = 0

    def write(self, text: str) -> None:
        self._text += text
        self._cursor += len(text)

    def set_cursor(self, pos: int) -> None:
        self._cursor = max(0, min(pos, len(self._text)))

    def save(self) -> Memento:
        return Memento({"text": self._text, "cursor": self._cursor})

    def restore(self, memento: Memento) -> None:
        state = memento.get_state()
        self._text = state["text"]
        self._cursor = state["cursor"]

    def __str__(self) -> str:
        return f"TextEditor(text={self._text!r}, cursor={self._cursor})"

class History:
    """Caretaker: holds mementos for undo."""
    def __init__(self):
        self._stack: list[Memento] = []

    def push(self, memento: Memento) -> None:
        self._stack.append(memento)

    def pop(self) -> Memento | None:
        return self._stack.pop() if self._stack else None


# Usage
editor = TextEditor()
history = History()

editor.write("Hello")
history.push(editor.save())
editor.write(" World")
history.push(editor.save())
editor.write("!")
print(editor)  # ... text='Hello World!'

editor.restore(history.pop())
print(editor)  # ... text='Hello World'
editor.restore(history.pop())
print(editor)  # ... text='Hello'
```

## Python example: narrow memento interface

Memento can expose almost nothing so only the originator can restore (e.g. pass a token or use a method that only the originator type can call):

```python
from dataclasses import dataclass

@dataclass
class EditorState:
    """Memento: just data. Caretaker holds it but doesn't need to understand it."""
    content: str
    selection_start: int
    selection_end: int

class Editor:
    def __init__(self):
        self.content = ""
        self.sel_start = 0
        self.sel_end = 0

    def create_memento(self) -> EditorState:
        return EditorState(self.content, self.sel_start, self.sel_end)

    def set_memento(self, state: EditorState) -> None:
        self.content = state.content
        self.sel_start = state.selection_start
        self.sel_end = state.selection_end
```

## Copy vs memento

For simple objects, a **deep copy** can act as a memento. The pattern is useful when:
- State is complex or expensive to copy and you want to be explicit.
- You want to hide the structure of state from the caretaker (encapsulation).
- You need to store metadata (e.g. timestamp) alongside the snapshot.

## Summary

| Pros | Cons |
|------|------|
| Preserves encapsulation (state not fully exposed) | Caretaker must not modify memento; can be memory-heavy |
| Simple undo/redo or checkpoints | |
| Originator stays in charge of its state shape | |

Use Memento when you need **undo, redo, or save/load** and want to **snapshot and restore object state** without exposing internals to the rest of the system.
