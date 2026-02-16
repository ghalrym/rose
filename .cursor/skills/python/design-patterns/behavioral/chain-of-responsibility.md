# Chain of Responsibility

Pass a request along a **chain of handlers**. Each handler either handles the request or forwards it to the next handler. Decouples sender from receiver and lets you add or reorder handlers.

## When to use

- More than one object may handle a request, and you don’t want the sender to know which one (e.g. middleware, event pipelines).
- You want to give several handlers a chance to process the request until one does.
- The set of handlers and their order should be configurable (add/remove/reorder).

## Structure

- **Handler**: Abstract class (or interface) with a method to handle the request and a reference to the next handler. May handle and stop, or pass to next.
- **ConcreteHandler**: Implements handling; optionally passes to successor.
- **Client**: Sends the request to the first handler in the chain.

## Python example: approval chain

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class Purchase:
    amount: float
    description: str

class ApprovalHandler(ABC):
    def __init__(self, next_handler: "ApprovalHandler | None" = None):
        self.next = next_handler

    def handle(self, purchase: Purchase) -> str:
        if self._can_handle(purchase):
            return self._process(purchase)
        if self.next:
            return self.next.handle(purchase)
        return "Denied"

    @abstractmethod
    def _can_handle(self, purchase: Purchase) -> bool:
        pass

    @abstractmethod
    def _process(self, purchase: Purchase) -> str:
        pass

class ManagerHandler(ApprovalHandler):
    MAX = 1000
    def _can_handle(self, purchase: Purchase) -> bool:
        return purchase.amount <= self.MAX
    def _process(self, purchase: Purchase) -> str:
        return f"Manager approved ${purchase.amount}"

class DirectorHandler(ApprovalHandler):
    MAX = 5000
    def _can_handle(self, purchase: Purchase) -> bool:
        return purchase.amount <= self.MAX
    def _process(self, purchase: Purchase) -> str:
        return f"Director approved ${purchase.amount}"

class VPHandler(ApprovalHandler):
    def _can_handle(self, purchase: Purchase) -> bool:
        return True
    def _process(self, purchase: Purchase) -> str:
        return f"VP approved ${purchase.amount}"


# Build chain: Manager -> Director -> VP
chain = ManagerHandler(DirectorHandler(VPHandler()))
print(chain.handle(Purchase(500, "Supplies")))   # Manager approved $500
print(chain.handle(Purchase(2500, "Equipment"))) # Director approved $2500
print(chain.handle(Purchase(10000, "Project")))  # VP approved $10000
```

## Python example: request middleware

```python
from typing import Callable, Any

Handler = Callable[[dict], dict | None]  # request -> response or None to continue

def logging_middleware(next_handler: Handler) -> Handler:
    def handler(request: dict) -> dict | None:
        print(f"Request: {request}")
        result = next_handler(request)
        print(f"Response: {result}")
        return result
    return handler

def auth_middleware(next_handler: Handler) -> Handler:
    def handler(request: dict) -> dict | None:
        if not request.get("token"):
            return {"error": "Unauthorized"}
        return next_handler(request)
    return handler

def rate_limit_middleware(next_handler: Handler) -> Handler:
    def handler(request: dict) -> dict | None:
        # check rate limit; if exceeded return 429
        return next_handler(request)
    return handler

def app(request: dict) -> dict:
    return {"data": "ok"}

# Chain: rate_limit -> auth -> logging -> app
pipeline = rate_limit_middleware(auth_middleware(logging_middleware(app)))
print(pipeline({"token": "abc"}))
```

## Python example: list of handlers (explicit chain)

```python
from abc import ABC, abstractmethod

class Handler(ABC):
    @abstractmethod
    def handle(self, request: str) -> str | None:
        """Return result if handled, None to pass to next."""
        pass

class HandlerChain:
    def __init__(self):
        self._handlers: list[Handler] = []

    def add(self, handler: Handler) -> "HandlerChain":
        self._handlers.append(handler)
        return self

    def handle(self, request: str) -> str:
        for h in self._handlers:
            result = h.handle(request)
            if result is not None:
                return result
        return "Unhandled"
```

## Summary

| Pros | Cons |
|------|------|
| Loose coupling: sender doesn’t know which handler runs | Request can go unhandled if chain ends |
| Easy to add or reorder handlers | |
| Single Responsibility per handler | |

Use Chain of Responsibility when **multiple handlers** might process a request and you want to **compose** them (middleware, approval workflows, event pipelines).
