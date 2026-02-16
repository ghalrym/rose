# Iterator

Provide a way to **access elements of a collection sequentially** without exposing its internal representation. Traversal logic lives in the iterator, not the collection.

## When to use

- You want to hide how a collection is stored (list, tree, graph) and offer a uniform way to traverse it.
- You want to support multiple traversal strategies for the same collection (e.g. in-order vs pre-order for a tree).
- You want a consistent interface for “get next element” across different collection types.

## Structure

- **Iterator**: Interface with `next()` (or `__next__`) and often `has_next()` (or catch `StopIteration`). Returns elements one by one.
- **ConcreteIterator**: Implements traversal for a specific collection (e.g. in-order tree iterator).
- **Aggregate**: Collection that can produce an iterator (e.g. `iter(collection)` or `get_iterator()`).
- **ConcreteAggregate**: The actual collection (list, tree, etc.).

## Python: protocol and built-in support

Python’s iteration protocol: an object is **iterable** if it has `__iter__()` returning an **iterator**; an **iterator** has `__next__()` and raises `StopIteration` when done. The built-in `iter()` and `for` use this.

```python
class CountDown:
    """Iterable that returns a custom iterator."""
    def __init__(self, start: int):
        self.start = start

    def __iter__(self) -> "CountDownIterator":
        return CountDownIterator(self.start)

class CountDownIterator:
    def __init__(self, start: int):
        self.current = start

    def __iter__(self):
        return self

    def __next__(self) -> int:
        if self.current < 0:
            raise StopIteration
        value = self.current
        self.current -= 1
        return value

for n in CountDown(3):
    print(n)  # 3, 2, 1, 0
```

## Python example: in-order tree iterator

```python
from dataclasses import dataclass
from typing import Iterator

@dataclass
class TreeNode:
    value: int
    left: "TreeNode | None" = None
    right: "TreeNode | None" = None

class InOrderIterator:
    """Iterator that yields BST nodes in-order (left, node, right)."""
    def __init__(self, root: TreeNode | None):
        self._stack: list[TreeNode] = []
        self._push_lefts(root)

    def _push_lefts(self, node: TreeNode | None) -> None:
        while node:
            self._stack.append(node)
            node = node.left

    def __iter__(self) -> "InOrderIterator":
        return self

    def __next__(self) -> int:
        if not self._stack:
            raise StopIteration
        node = self._stack.pop()
        self._push_lefts(node.right)
        return node.value

class BinarySearchTree:
    def __init__(self, root: TreeNode | None = None):
        self.root = root

    def __iter__(self) -> Iterator[int]:
        return InOrderIterator(self.root)


# Usage
root = TreeNode(5, TreeNode(3, TreeNode(1), TreeNode(4)), TreeNode(7))
bst = BinarySearchTree(root)
print(list(bst))  # [1, 3, 4, 5, 7]
```

## Python example: generator as iterator

Generators are the usual way to implement iterators in Python; they implement the iterator protocol automatically:

```python
def in_order(node: TreeNode | None):
    if node is None:
        return
    yield from in_order(node.left)
    yield node.value
    yield from in_order(node.right)

# Usage
for value in in_order(root):
    print(value)
```

## Filtering / mapping iterators

Wrap an iterator to transform or filter without materializing the whole collection:

```python
def filter_even(it):
    for x in it:
        if x % 2 == 0:
            yield x

def map_square(it):
    for x in it:
        yield x * x

numbers = [1, 2, 3, 4, 5]
for v in map_square(filter_even(numbers)):
    print(v)  # 4, 16
```

## Summary

| Pros | Cons |
|------|------|
| Hide collection internals | Extra iterator class (or generator) per traversal type |
| Uniform traversal interface | |
| Lazy: one element at a time | |

In Python, prefer **generators** (`yield`) for custom iterators unless you need a full class (e.g. to implement `__reversed__` or hold complex state). Use the **built-in protocol** (`__iter__`, `__next__`, `StopIteration`) for custom collections.
