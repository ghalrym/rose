# Visitor

Represent an **operation to be performed on elements of an object structure**. Visitor lets you define a new operation without changing the classes of the elements on which it operates. Useful when you have a stable set of element types and a growing set of operations.

## When to use

- You have a structure of element types (e.g. AST nodes, UI nodes) and want to add new **operations** (e.g. “export to JSON”, “type check”) without adding a method to every element class.
- The set of element classes is stable or changes rarely; the set of operations changes often.
- You want to keep operation logic in one place (the visitor) instead of scattering it across element classes.

## Structure

- **Visitor**: Declares a `visit(ElementX)` for each concrete element type. Each element type has a corresponding visit method.
- **ConcreteVisitor**: Implements each visit method with the operation logic for that element.
- **Element**: Defines `accept(Visitor)` that calls `visitor.visit(self)` so the right overload runs.
- **ConcreteElement**: Implements `accept`; the visitor then does the operation for this type.

## Python example: expression AST and visitors

```python
from abc import ABC, abstractmethod

class Expr(ABC):
    @abstractmethod
    def accept(self, visitor: "Visitor") -> None:
        pass

class Literal(Expr):
    def __init__(self, value: int):
        self.value = value
    def accept(self, visitor: "Visitor") -> None:
        visitor.visit_literal(self)

class Binary(Expr):
    def __init__(self, op: str, left: Expr, right: Expr):
        self.op = op
        self.left = left
        self.right = right
    def accept(self, visitor: "Visitor") -> None:
        visitor.visit_binary(self)

class Visitor(ABC):
    def visit_literal(self, node: Literal) -> None:
        pass
    def visit_binary(self, node: Binary) -> None:
        pass

class EvalVisitor(Visitor):
    """Operation: evaluate expression."""
    def __init__(self):
        self.result: int = 0

    def visit_literal(self, node: Literal) -> None:
        self.result = node.value

    def visit_binary(self, node: Binary) -> None:
        node.left.accept(self)
        left_val = self.result
        node.right.accept(self)
        right_val = self.result
        if node.op == "+":
            self.result = left_val + right_val
        elif node.op == "*":
            self.result = left_val * right_val

class PrintVisitor(Visitor):
    """Operation: print expression."""
    def visit_literal(self, node: Literal) -> None:
        print(node.value, end="")

    def visit_binary(self, node: Binary) -> None:
        print("(", end="")
        node.left.accept(self)
        print(f" {node.op} ", end="")
        node.right.accept(self)
        print(")", end="")


# Usage: 1 + 2 * 3
ast = Binary("+", Literal(1), Binary("*", Literal(2), Literal(3)))
eval_visitor = EvalVisitor()
ast.accept(eval_visitor)
print(eval_visitor.result)  # 7

PrintVisitor().visit_binary(ast)
# (1 + (2 * 3))
```

## Python example: double dispatch with single visit method

If you’re okay with the visitor having one `visit` that dispatches by type, you can use a single method and `type()` or a small registry:

```python
from abc import ABC, abstractmethod

class Node(ABC):
    @abstractmethod
    def accept(self, visitor: "NodeVisitor") -> None:
        pass

class A(Node):
    def accept(self, visitor: "NodeVisitor") -> None:
        visitor.visit(self)

class B(Node):
    def accept(self, visitor: "NodeVisitor") -> None:
        visitor.visit(self)

class NodeVisitor(ABC):
    def visit(self, node: Node) -> None:
        method = getattr(self, f"visit_{type(node).__name__}", self.generic_visit)
        method(node)
    def generic_visit(self, node: Node) -> None:
        print(f"Unknown node: {type(node).__name__}")

class MyVisitor(NodeVisitor):
    def visit_A(self, node: A) -> None:
        print("Visited A")
    def visit_B(self, node: B) -> None:
        print("Visited B")
```

## When to use Visitor

- **Stable element hierarchy**, **many operations** → Visitor keeps each operation in one visitor class.
- **Unstable element hierarchy** (new node types often) → Adding a method per element is painful; Visitor forces you to update every visitor for each new type.

Trade-off: adding a new **operation** = new visitor; adding a new **element type** = update all visitors and the element’s `accept`. Choose when operations outnumber element types and change more often.

## Summary

| Pros | Cons |
|------|------|
| New operations without changing element classes | Adding a new element type requires updating all visitors |
| Operation logic grouped in one visitor | More boilerplate (accept + visit_X per type) |
| | Can be harder to follow than simple methods on elements |

Use Visitor when you have a **fixed or slow-changing set of element types** and a **growing set of operations** (e.g. AST evaluation, printing, type checking, serialization).
