# Proxy

Provide a **surrogate or placeholder** for another object to control access to it. The proxy has the same interface as the real object so the client uses it transparently.

## When to use

- **Lazy initialization**: Create the real object only when first needed.
- **Access control**: Check permissions before forwarding to the real object.
- **Logging / auditing**: Log calls or parameters before or after delegating.
- **Remote proxy**: Represent an object in another address space (e.g. RPC stub).
- **Caching**: Return cached result when the real object is expensive to call.

## Structure

- **Subject**: Interface that both the real object and the proxy implement.
- **RealSubject**: The actual object that does the work.
- **Proxy**: Implements Subject; holds a reference to RealSubject (or creates it on demand); forwards requests after doing its own work (lazy init, check, log, cache).

## Python example: lazy initialization proxy

```python
from abc import ABC, abstractmethod

class Database(ABC):
    """Subject."""
    @abstractmethod
    def query(self, sql: str) -> list[dict]:
        pass

class RealDatabase(Database):
    """RealSubject: expensive to create (e.g. opens connection)."""
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        print("RealDatabase: connecting...")

    def query(self, sql: str) -> list[dict]:
        return [{"row": 1}]

class LazyDatabaseProxy(Database):
    """Proxy: creates RealDatabase only on first use."""
    def __init__(self, connection_string: str):
        self._connection_string = connection_string
        self._real: Database | None = None

    def _get_real(self) -> Database:
        if self._real is None:
            self._real = RealDatabase(self._connection_string)
        return self._real

    def query(self, sql: str) -> list[dict]:
        return self._get_real().query(sql)


# Usage: proxy is created quickly; real DB only when first query
proxy = LazyDatabaseProxy("postgres://localhost/db")
# No "connecting..." yet
result = proxy.query("SELECT 1")  # Now connects and runs query
```

## Python example: protection proxy (access control)

```python
from abc import ABC, abstractmethod

class Document(ABC):
    @abstractmethod
    def read(self) -> str:
        pass

    @abstractmethod
    def write(self, content: str) -> None:
        pass

class RealDocument(Document):
    def __init__(self, filename: str):
        self.filename = filename
        self._content = ""

    def read(self) -> str:
        return self._content

    def write(self, content: str) -> None:
        self._content = content

class ProtectedDocumentProxy(Document):
    def __init__(self, document: Document, user_role: str):
        self._document = document
        self._user_role = user_role

    def read(self) -> str:
        return self._document.read()

    def write(self, content: str) -> None:
        if self._user_role != "admin":
            raise PermissionError("Only admin can write")
        self._document.write(content)


doc = ProtectedDocumentProxy(RealDocument("report.txt"), "user")
doc.read()   # OK
doc.write("x")  # PermissionError
```

## Python example: caching proxy

```python
from typing import Any

class RemoteService:
    def fetch(self, key: str) -> str:
        print(f"RemoteService.fetch({key})")
        return f"data for {key}"

class CachingProxy:
    def __init__(self, service: RemoteService):
        self._service = service
        self._cache: dict[str, str] = {}

    def fetch(self, key: str) -> str:
        if key not in self._cache:
            self._cache[key] = self._service.fetch(key)
        return self._cache[key]


svc = CachingProxy(RemoteService())
print(svc.fetch("user:1"))  # RemoteService.fetch(user:1) ... data for user:1
print(svc.fetch("user:1"))  # (no print — from cache)
```

## Python: built-in proxy-like patterns

- **`property`**: Intercept attribute access; use for lazy init, validation, or computed attributes.
- **`__getattr__`**: Forward attribute access to a wrapped object (proxy-like).
- **`functools.lru_cache`**: Caches function results (cache proxy for a function).

```python
class LazyExpensive:
    @property
    def value(self) -> str:
        if not hasattr(self, "_value"):
            self._value = self._compute()
        return self._value
    def _compute(self) -> str:
        return "expensive result"
```

## Summary

| Pros | Cons |
|------|------|
| Control access without changing the real object | Extra layer; can add latency |
| Lazy init, caching, logging, protection in one place | |
| Same interface as real object (transparent to client) | |

Use Proxy when you need **controlled or delayed access** to an object (lazy init, caching, permissions, logging) and want to keep the **same interface** as the real subject.
