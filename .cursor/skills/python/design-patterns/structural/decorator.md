# Decorator

Attach **additional responsibilities** to an object dynamically. Decorators provide a flexible alternative to subclassing for extending behavior.

## When to use

- You need to add behavior to individual objects (e.g. logging, caching, auth) without affecting other instances of the same class.
- Subclassing would lead to many combinations (e.g. LoggedCachedStream, CachedStream, LoggedStream…); decorators can be stacked.
- You want to add/remove responsibilities at runtime.

## Structure

- **Component**: Interface for the object that can have responsibilities added.
- **ConcreteComponent**: Default implementation.
- **Decorator**: Holds a reference to a Component and implements the same interface; usually forwards to the wrapped component and adds behavior before/after.
- **ConcreteDecorator**: Adds specific behavior (e.g. logging, caching).

## Python example: stream decorators

```python
from abc import ABC, abstractmethod

class Stream(ABC):
    """Component."""
    @abstractmethod
    def write(self, data: str) -> None:
        pass

    @abstractmethod
    def read(self) -> str:
        pass

class FileStream(Stream):
    """ConcreteComponent."""
    def __init__(self, filename: str):
        self.filename = filename
        self._buffer: list[str] = []

    def write(self, data: str) -> None:
        self._buffer.append(data)

    def read(self) -> str:
        return "".join(self._buffer)

class StreamDecorator(Stream):
    """Decorator: wraps another Stream."""
    def __init__(self, wrapped: Stream):
        self._wrapped = wrapped

    def write(self, data: str) -> None:
        self._wrapped.write(data)

    def read(self) -> str:
        return self._wrapped.read()

class CompressDecorator(StreamDecorator):
    """Adds compression (simulated)."""
    def write(self, data: str) -> None:
        compressed = f"[compressed]{data}[/compressed]"
        self._wrapped.write(compressed)

    def read(self) -> str:
        raw = self._wrapped.read()
        return raw.replace("[compressed]", "").replace("[/compressed]", "")

class LogDecorator(StreamDecorator):
    """Adds logging."""
    def write(self, data: str) -> None:
        print(f"LOG: writing {len(data)} chars")
        self._wrapped.write(data)


# Usage: stack decorators
stream: Stream = FileStream("out.txt")
stream = LogDecorator(stream)
stream = CompressDecorator(stream)
stream.write("Hello")
stream.read()
```

## Python example: function decorators (the common case)

The language’s `@decorator` syntax is the same idea: wrap a callable to add behavior.

```python
import functools

def log_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}({args}, {kwargs})")
        result = func(*args, **kwargs)
        print(f"  -> {result}")
        return result
    return wrapper

def cache(maxsize=128):
    def decorator(func):
        _cache = {}
        @functools.wraps(func)
        def wrapper(*args):
            if args in _cache:
                return _cache[args]
            result = func(*args)
            if len(_cache) >= maxsize:
                _cache.pop(next(iter(_cache)))
            _cache[args] = result
            return result
        return wrapper
    return decorator

@log_calls
@cache(maxsize=2)
def expensive(n: int) -> int:
    return n * n

expensive(3)  # Calling expensive((3,), {}) -> 9
expensive(3)  # (from cache, no "Calling" if you don't log cache hit)
```

## Python example: retry decorator

```python
import functools
import time

def retry(max_attempts: int = 3, delay: float = 1.0):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
            raise last_error
        return wrapper
    return decorator

@retry(max_attempts=3, delay=0.1)
def flaky_request():
    # might fail sometimes
    ...
```

## Summary

| Pros | Cons |
|------|------|
| Add behavior without subclassing | Many small classes/decorators |
| Stack and combine behaviors | Order of decorators can matter |
| Single Responsibility per decorator | |

Use Decorator when you want to **add optional, stackable behavior** to objects or functions (logging, caching, retry, auth) without changing the core type.
