# Facade

Provide a **unified, simple interface** to a set of interfaces in a subsystem. Facade defines a higher-level API that makes the subsystem easier to use.

## When to use

- You have a complex subsystem (many classes, steps, or dependencies) and want a single entry point for common tasks.
- You want to decouple client code from the internals of the subsystem so you can change the subsystem without changing clients.
- You want to layer the system: facade for “simple” use, direct access to subsystems when needed.

## Structure

- **Facade**: One class (or module) that knows how to use the subsystem; exposes a small set of methods that do common workflows.
- **Subsystem classes**: Existing classes that do the real work; the facade calls them in the right order and with the right parameters.

## Python example: video conversion facade

Subsystem: file reader, codec, and file writer. Facade: “convert file” in one call.

```python
# --- Subsystem (simplified) ---
class FileReader:
    def read(self, path: str) -> bytes:
        with open(path, "rb") as f:
            return f.read()

class Codec:
    def decode(self, data: bytes, format: str) -> str:
        return f"decoded_{format}:{len(data)}_bytes"

    def encode(self, content: str, format: str) -> bytes:
        return f"encoded_{format}:{content}".encode()

class FileWriter:
    def write(self, path: str, data: bytes) -> None:
        with open(path, "wb") as f:
            f.write(data)


# --- Facade ---
class VideoConverter:
    """Single entry point for the conversion workflow."""
    def __init__(self):
        self._reader = FileReader()
        self._codec = Codec()
        self._writer = FileWriter()

    def convert(self, input_path: str, output_path: str, output_format: str = "mp4") -> str:
        data = self._reader.read(input_path)
        content = self._codec.decode(data, "source")
        encoded = self._codec.encode(content, output_format)
        self._writer.write(output_path, encoded)
        return output_path


# Client uses only the facade
converter = VideoConverter()
converter.convert("input.avi", "output.mp4")
```

## Python example: order placement facade

Subsystem: inventory, payment, shipping, notification. Facade: “place order”.

```python
# --- Subsystem ---
class InventoryService:
    def reserve(self, product_id: str, quantity: int) -> bool:
        print(f"Reserved {quantity} of {product_id}")
        return True
    def release(self, product_id: str, quantity: int) -> None:
        print(f"Released {quantity} of {product_id}")

class PaymentService:
    def charge(self, amount_cents: int, token: str) -> str:
        print(f"Charged {amount_cents} cents")
        return "txn_123"

class ShippingService:
    def schedule(self, order_id: str, address: dict) -> str:
        print(f"Scheduled shipping for order {order_id}")
        return "tracking_456"

class NotificationService:
    def send_order_confirmation(self, order_id: str, email: str) -> None:
        print(f"Sent confirmation for {order_id} to {email}")


# --- Facade ---
class OrderService:
    def __init__(self):
        self.inventory = InventoryService()
        self.payment = PaymentService()
        self.shipping = ShippingService()
        self.notifications = NotificationService()

    def place_order(
        self,
        product_id: str,
        quantity: int,
        payment_token: str,
        price_cents: int,
        email: str,
        address: dict,
    ) -> str:
        order_id = f"ord_{product_id}_{quantity}"
        if not self.inventory.reserve(product_id, quantity):
            raise ValueError("Insufficient inventory")
        try:
            self.payment.charge(price_cents, payment_token)
            self.shipping.schedule(order_id, address)
            self.notifications.send_order_confirmation(order_id, email)
            return order_id
        except Exception:
            self.inventory.release(product_id, quantity)
            raise


# Client
order_svc = OrderService()
order_id = order_svc.place_order(
    "prod_1", 2, "tok_xyz", 5999, "user@example.com", {"city": "NYC"}
)
```

## Facade vs Adapter

- **Facade**: Defines a **new, simpler** interface to a subsystem. You’re not changing an existing interface; you’re providing a convenience layer.
- **Adapter**: Makes **one existing** interface conform to another. You’re translating between two interfaces that already exist.

## Summary

| Pros | Cons |
|------|------|
| Simpler API for common use cases | Facade can become a “god” class if it grows too much |
| Decouples clients from subsystem details | |
| One place to change workflow logic | |

Use Facade when you have a **complex or multi-step subsystem** and want a **single, clear entry point** for the most common operations.
