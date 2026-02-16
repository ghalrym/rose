# Template Method

Define the **skeleton of an algorithm** in a base class, deferring some steps to subclasses. Subclasses override specific steps without changing the algorithm’s structure.

## When to use

- You have an algorithm with invariant steps and a few steps that vary (e.g. “read data → transform → write”; only transform varies).
- You want to avoid duplicating the overall flow in multiple places; put it once in a template method and override the variable parts.
- You want to control extension points so subclasses can’t break the overall flow.

## Structure

- **AbstractClass**: Defines a **template method** that calls abstract or hook methods in a fixed order. The template method implements the algorithm skeleton.
- **ConcreteClass**: Implements the abstract/hook methods with concrete behavior.

## Python example: data processing pipeline

```python
from abc import ABC, abstractmethod

class DataProcessor(ABC):
    """Template method: load -> process -> save. Subclasses define process."""

    def run(self, path: str) -> None:
        """Template method."""
        data = self.load(path)
        processed = self.process(data)
        self.save(processed)

    def load(self, path: str) -> str:
        with open(path) as f:
            return f.read()

    @abstractmethod
    def process(self, data: str) -> str:
        pass

    def save(self, data: str) -> None:
        print(f"Saved: {len(data)} chars")

class UpperCaseProcessor(DataProcessor):
    def process(self, data: str) -> str:
        return data.upper()

class TrimProcessor(DataProcessor):
    def process(self, data: str) -> str:
        return data.strip()


# Usage
# processor = UpperCaseProcessor()
# processor.run("input.txt")  # load -> process (upper) -> save
```

## Python example: hook methods

Some steps have a default implementation (hook); subclasses override only when needed:

```python
from abc import ABC, abstractmethod

class ReportGenerator(ABC):
    def generate(self) -> str:
        """Template method."""
        header = self.get_header()
        body = self.get_body()
        footer = self.get_footer()  # hook with default
        return f"{header}\n{body}\n{footer}"

    @abstractmethod
    def get_header(self) -> str:
        pass

    @abstractmethod
    def get_body(self) -> str:
        pass

    def get_footer(self) -> str:
        """Hook: optional override."""
        return "--- End of Report ---"

class SalesReport(ReportGenerator):
    def get_header(self) -> str:
        return "Sales Report"
    def get_body(self) -> str:
        return "Revenue: $1000"
    def get_footer(self) -> str:
        return "Confidential - Sales Team Only"
```

## Python example: connection template

```python
from abc import ABC, abstractmethod

class ConnectionTemplate(ABC):
    def execute(self) -> None:
        """Template: connect -> do_work -> disconnect."""
        self.connect()
        try:
            self.do_work()
        finally:
            self.disconnect()

    def connect(self) -> None:
        print("Default: opening connection")

    @abstractmethod
    def do_work(self) -> None:
        pass

    def disconnect(self) -> None:
        print("Default: closing connection")

class HTTPConnection(ConnectionTemplate):
    def do_work(self) -> None:
        print("HTTP request/response")

class DBConnection(ConnectionTemplate):
    def connect(self) -> None:
        print("DB: connect")
    def do_work(self) -> None:
        print("DB: query")
    def disconnect(self) -> None:
        print("DB: disconnect")
```

## Template Method vs Strategy

- **Template Method**: Flow is fixed in the base class; subclasses fill in steps. Inheritance-based.
- **Strategy**: The whole algorithm is pluggable (passed in). Composition-based.

Use Template Method when the **structure of the algorithm is fixed** and only **steps vary**; use Strategy when you need to **swap entire algorithms**.

## Summary

| Pros | Cons |
|------|------|
| No duplication of algorithm structure | Can lead to deep subclass hierarchies |
| Extension only at defined points | |
| Common flow in one place | |

Use Template Method when you have a **fixed algorithm skeleton** and **variable steps** that subclasses should provide.
