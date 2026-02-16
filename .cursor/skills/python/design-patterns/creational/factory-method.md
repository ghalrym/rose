# Factory Method

Define an interface for creating an object, but let subclasses decide which class to instantiate. Creation is delegated to a method that can be overridden.

## When to use

- You can’t know the exact class of the object until runtime (e.g. based on config or user choice).
- You want to centralize creation logic so callers don’t depend on concrete classes.
- Subclasses should provide their own product type (parallel class hierarchies).

## Structure

- **Creator** (base): Declares a factory method that returns a **Product**. May call it in other methods.
- **ConcreteCreator**: Overrides the factory method to return a **ConcreteProduct**.
- **Product** (interface): Type returned by the factory method.
- **ConcreteProduct**: Actual implementation.

## Python example: document exporters

```python
from abc import ABC, abstractmethod

class ExportFormat(ABC):
    """Product interface."""
    @abstractmethod
    def export(self, data: dict) -> str:
        pass

class PDFExport(ExportFormat):
    def export(self, data: dict) -> str:
        return f"[PDF] {data}"

class JSONExport(ExportFormat):
    def export(self, data: dict) -> str:
        import json
        return json.dumps(data)

class CSVExport(ExportFormat):
    def export(self, data: dict) -> str:
        return ",".join(f"{k}:{v}" for k, v in data.items())


class DocumentExporter(ABC):
    """Creator: uses factory method to get the right export format."""
    def export_document(self, data: dict) -> str:
        exporter = self._create_exporter()
        return exporter.export(data)

    @abstractmethod
    def _create_exporter(self) -> ExportFormat:
        """Factory method."""
        pass

class PDFDocumentExporter(DocumentExporter):
    def _create_exporter(self) -> ExportFormat:
        return PDFExport()

class JSONDocumentExporter(DocumentExporter):
    def _create_exporter(self) -> ExportFormat:
        return JSONExport()


# Usage
data = {"title": "Report", "pages": 10}
pdf_exporter = PDFDocumentExporter()
print(pdf_exporter.export_document(data))  # [PDF] {'title': 'Report', 'pages': 10}

json_exporter = JSONDocumentExporter()
print(json_exporter.export_document(data))  # {"title": "Report", "pages": 10}
```

## Simpler: factory function (no subclasses)

Often you don’t need a class hierarchy—a function that returns the right type is enough:

```python
def create_exporter(format_name: str) -> ExportFormat:
    exporters = {
        "pdf": PDFExport,
        "json": JSONExport,
        "csv": CSVExport,
    }
    cls = exporters.get(format_name)
    if not cls:
        raise ValueError(f"Unknown format: {format_name}")
    return cls()

# Usage
exporter = create_exporter("json")
print(exporter.export({"a": 1}))
```

## Python example: parser factory by file type

```python
from pathlib import Path

class Parser(ABC):
    @abstractmethod
    def parse(self, path: Path) -> dict:
        pass

class JSONParser(Parser):
    def parse(self, path: Path) -> dict:
        import json
        return json.loads(path.read_text())

class YAMLParser(Parser):
    def parse(self, path: Path) -> dict:
        import yaml
        return yaml.safe_load(path.read_text())

def create_parser(path: Path) -> Parser:
    """Factory function by file extension."""
    suffix = path.suffix.lower()
    if suffix == ".json":
        return JSONParser()
    if suffix in (".yaml", ".yml"):
        return YAMLParser()
    raise ValueError(f"No parser for {suffix}")
```

## Summary

| Pros | Cons |
|------|------|
| Loose coupling to concrete product classes | Extra classes (creator/product hierarchy) |
| Single place for creation logic | |
| Easy to add new product types | |

Use a **factory function** when you don’t need multiple creator subtypes; use **factory method** when creation varies by subclass.
