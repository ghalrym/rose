# Adapter

Convert the interface of a class into another interface clients expect. Lets classes work together that couldn’t otherwise because of incompatible interfaces.

## When to use

- You want to use an existing class (or third-party library) but its interface doesn’t match what your code expects.
- You don’t control the source of the existing class and can’t change it.
- You want to reuse several existing classes with different interfaces through a common interface.

## Structure

- **Target**: The interface your client code depends on.
- **Adaptee**: The existing class with the “wrong” interface.
- **Adapter**: Implements the Target interface and holds (or subclasses) the Adaptee; translates calls from Target to Adaptee.

## Python example: external payment API

Your app expects a simple interface; the external library has a different one:

```python
from abc import ABC, abstractmethod

# --- Target: what our app expects ---
class PaymentProcessor(ABC):
    @abstractmethod
    def charge(self, amount_cents: int, currency: str, token: str) -> str:
        """Returns transaction_id on success."""
        pass

# --- Adaptee: external library we can't change ---
class LegacyPaymentGateway:
    """Simulates a third-party class with a different API."""
    def process_payment(
        self,
        amount: float,           # dollars, not cents
        curr: str,
        card_token: str,
        idempotency_key: str,
    ) -> dict:
        return {
            "success": True,
            "transaction_ref": f"txn_{idempotency_key}",
        }

# --- Adapter: wraps Adaptee, implements Target ---
class LegacyPaymentAdapter(PaymentProcessor):
    def __init__(self, gateway: LegacyPaymentGateway):
        self._gateway = gateway

    def charge(self, amount_cents: int, currency: str, token: str) -> str:
        amount_dollars = amount_cents / 100.0
        import uuid
        result = self._gateway.process_payment(
            amount=amount_dollars,
            curr=currency,
            card_token=token,
            idempotency_key=str(uuid.uuid4()),
        )
        if not result.get("success"):
            raise RuntimeError("Payment failed")
        return result["transaction_ref"]


# --- Client code uses only PaymentProcessor ---
def checkout(processor: PaymentProcessor, amount_cents: int, token: str) -> None:
    txn_id = processor.charge(amount_cents, "USD", token)
    print(f"Charged successfully: {txn_id}")

# Usage
gateway = LegacyPaymentGateway()
adapter = LegacyPaymentAdapter(gateway)
checkout(adapter, 1999, "tok_abc")  # $19.99
```

## Python example: file-like adapter for a REST API

Your code expects something with `read()` / `write()`; the API has `get()` / `put()`:

```python
from typing import Protocol

class Readable(Protocol):
    def read(self) -> str: ...

# --- Adaptee (simulated) ---
class RemoteStorageAPI:
    def get(self, path: str) -> bytes:
        return b"content from api"
    def put(self, path: str, data: bytes) -> None:
        pass

# --- Adapter: make RemoteStorageAPI look like a file-like for reading ---
class RemoteFileAdapter:
    def __init__(self, api: RemoteStorageAPI, path: str):
        self._api = api
        self._path = path

    def read(self) -> str:
        return self._api.get(self._path).decode("utf-8")

    def write(self, content: str) -> None:
        self._api.put(self._path, content.encode("utf-8"))

# Client that only needs read()
def process_file(source: Readable) -> str:
    return source.read().upper()

adapter = RemoteFileAdapter(RemoteStorageAPI(), "/doc.txt")
print(process_file(adapter))
```

## Object adapter vs class adapter

- **Object adapter**: Adapter holds an instance of the adaptee (composition). Shown above; preferred in Python.
- **Class adapter**: Adapter inherits from both Target and Adaptee. Requires multiple inheritance; in Python you can do it but composition is usually clearer.

## Summary

| Pros | Cons |
|------|------|
| Reuse existing/third-party code | Extra adapter class per target/adaptee pair |
| Single Responsibility: translation in one place | |
| Client stays independent of adaptee API | |

Use Adapter when you must **talk to an interface you can’t change** and want **one place** that translates to the interface your code expects.
