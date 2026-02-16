# Singleton

Ensure a class has only one instance and provide a global access point to it.

## When to use

- Exactly one instance must coordinate actions (e.g. config, connection pool, logger).
- That instance must be reachable from many places.

**Caution**: Singletons can hide dependencies and make testing harder. Prefer **dependency injection**: create one instance and pass it in. Use Singleton only when a true global single instance is required (e.g. process-wide config loaded once).

## Structure

- Private constructor (so others can’t `new` it).
- Static/class-level method or property that returns the single instance.
- Instance created lazily on first access (optional).

## Python example

```python
from threading import Lock

class DatabaseConnection:
    _instance = None
    _lock = Lock()

    def __new__(cls, connection_string: str = ""):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, connection_string: str = ""):
        if self._initialized:
            return
        self.connection_string = connection_string
        self._initialized = True

    def connect(self) -> str:
        return f"Connected to {self.connection_string}"


# Usage
db1 = DatabaseConnection("postgres://localhost/mydb")
db2 = DatabaseConnection("postgres://other/db")
assert db1 is db2
print(db1.connect())  # Connected to postgres://localhost/mydb
```

## Simpler alternative: module-level instance

In Python, a module is loaded once, so a module-level object is effectively a singleton:

```python
# config.py
class _AppConfig:
    def __init__(self):
        self.debug = False
        self.host = "localhost"

config = _AppConfig()
```

```python
# other_module.py
from config import config
config.debug = True
```

## Using `functools.cache` for a factory singleton

If the “singleton” is the return value of a function (e.g. “get DB connection”), one instance per set of arguments:

```python
from functools import cache

@cache
def get_db(connection_string: str):
    return create_connection(connection_string)
```

## Summary

| Pros | Cons |
|------|------|
| Single instance, controlled access | Harder to test (global state) |
| Lazy initialization possible | Hidden coupling |
| | Not needed if you use DI |

Prefer passing the dependency (e.g. config or DB) into constructors or FastAPI `Depends()` instead of a true Singleton when you can.
