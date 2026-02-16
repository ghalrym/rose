# Docstrings

Use docstrings for public modules, classes, and functions. Each docstring must include:

1. **Brief definition** – One short sentence describing what the thing does.
2. **Args** – For each parameter: name, type/meaning, and any constraint or default behavior.
3. **Returns** – What is returned (type and meaning); if `None`, say so.
4. **Raises** – Every exception type the callable can raise, and when (briefly).

**Function/method template:**

```python
def compute_total(items: list[LineItem], tax_rate: float) -> Decimal:
    """Compute total price including tax.

    Args:
        items: List of line items to sum.
        tax_rate: Tax rate in [0, 1], e.g. 0.08 for 8%.

    Returns:
        Total price including tax as a Decimal.

    Raises:
        ValueError: If tax_rate is not in [0, 1].
    """
```

**Class template:**

```python
class OrderProcessor:
    """Processes orders and updates inventory.

    Attributes:
        inventory: Current inventory state (mutated in place).
    """

    def __init__(self, inventory: Inventory) -> None:
        """Initialize with an inventory instance.

        Args:
            inventory: The inventory to update.

        Returns:
            None.

        Raises:
            None.
        """
```

Omit "Raises" or "Returns: None" only when there are no exceptions or the return is trivially `None` and the brief definition already says so; when in doubt, include them.
