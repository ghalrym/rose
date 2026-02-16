# Strategy

Define a **family of algorithms**, encapsulate each one, and make them **interchangeable**. Strategy lets the algorithm vary independently from the clients that use it.

## When to use

- You have several ways to do the same thing (e.g. sort by different keys, different pricing rules, different serialization formats) and want to switch at runtime or per use case.
- You want to avoid conditional logic that selects among algorithms; pass the algorithm instead.
- You want to isolate algorithm logic so it’s easier to test and extend.

## Structure

- **Context**: Uses a **Strategy** to do work; holds a reference to it and can replace it.
- **Strategy**: Interface for the algorithm (e.g. `execute(data)` or `compute(x, y)`).
- **ConcreteStrategy**: Each class implements one variant of the algorithm.

## Python example: pricing strategies

```python
from abc import ABC, abstractmethod

class PricingStrategy(ABC):
    @abstractmethod
    def price(self, base_price: float, quantity: int) -> float:
        pass

class NormalPricing(PricingStrategy):
    def price(self, base_price: float, quantity: int) -> float:
        return base_price * quantity

class BulkDiscountPricing(PricingStrategy):
    def __init__(self, threshold: int, discount_pct: float):
        self.threshold = threshold
        self.discount_pct = discount_pct

    def price(self, base_price: float, quantity: int) -> float:
        total = base_price * quantity
        if quantity >= self.threshold:
            total *= (1 - self.discount_pct / 100)
        return total

class SubscriptionPricing(PricingStrategy):
    def price(self, base_price: float, quantity: int) -> float:
        return base_price * 0.9 * quantity  # 10% off

class Order:
    """Context: uses a pricing strategy."""
    def __init__(self, strategy: PricingStrategy):
        self.strategy = strategy
        self.items: list[tuple[float, int]] = []  # (base_price, quantity)

    def add_item(self, base_price: float, quantity: int) -> None:
        self.items.append((base_price, quantity))

    def total(self) -> float:
        return sum(
            self.strategy.price(price, qty)
            for price, qty in self.items
        )


# Usage
order = Order(NormalPricing())
order.add_item(10.0, 5)
print(order.total())  # 50.0

order.strategy = BulkDiscountPricing(threshold=5, discount_pct=10)
print(order.total())  # 45.0
```

## Python example: validation strategies

```python
from abc import ABC, abstractmethod

class ValidationStrategy(ABC):
    @abstractmethod
    def validate(self, value: str) -> tuple[bool, str]:
        """Returns (is_valid, error_message)."""
        pass

class NonEmptyValidation(ValidationStrategy):
    def validate(self, value: str) -> tuple[bool, str]:
        if not value.strip():
            return False, "Cannot be empty"
        return True, ""

class EmailValidation(ValidationStrategy):
    def validate(self, value: str) -> tuple[bool, str]:
        if "@" not in value or "." not in value.split("@")[-1]:
            return False, "Invalid email"
        return True, ""

class MinLengthValidation(ValidationStrategy):
    def __init__(self, min_len: int):
        self.min_len = min_len
    def validate(self, value: str) -> tuple[bool, str]:
        if len(value) < self.min_len:
            return False, f"Min length {self.min_len}"
        return True, ""

def validate_field(value: str, strategies: list[ValidationStrategy]) -> list[str]:
    errors = []
    for s in strategies:
        ok, msg = s.validate(value)
        if not ok:
            errors.append(msg)
    return errors

# Usage
errs = validate_field("a", [NonEmptyValidation(), MinLengthValidation(3)])
print(errs)  # ['Min length 3']
```

## Python: strategy as a callable

When the “algorithm” is a single function, you can pass a function instead of an object:

```python
from typing import Callable

def sort_by_name(items: list[dict]) -> list[dict]:
    return sorted(items, key=lambda x: x["name"])

def sort_by_date(items: list[dict]) -> list[dict]:
    return sorted(items, key=lambda x: x["created_at"])

def process(items: list[dict], sorter: Callable[[list[dict]], list[dict]]) -> list[dict]:
    return sorter(items)

process(users, sort_by_name)
process(users, sort_by_date)
```

Use a **class** when the strategy needs configuration (e.g. threshold, discount) or multiple methods; use a **callable** when it’s a single pure function.

## Summary

| Pros | Cons |
|------|------|
| Swap algorithms at runtime | More types (context + strategy hierarchy) |
| Isolates algorithm logic | |
| Easy to add new strategies | |

Use Strategy when you have **multiple interchangeable algorithms** and want to **pass the one to use** instead of branching on a type or flag.
