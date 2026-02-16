# State

Allow an object to **alter its behavior when its internal state changes**. The object will appear to change its class. Encapsulate state-specific behavior in separate classes and delegate to the current state.

## When to use

- An object’s behavior depends on its state and that behavior changes frequently (e.g. TCP connection: listen, established, closed).
- You have a lot of conditionals that switch on the same state variable; replacing them with state objects can simplify the code.
- State transitions are clear and you want to represent each state explicitly.

## Structure

- **Context**: Holds the current **State**; delegates state-dependent requests to it. May pass itself to the state for transitions.
- **State**: Abstract interface for state-specific behavior (e.g. `handle()`).
- **ConcreteState**: Each subclass implements behavior for one state and can trigger transitions (set context’s state to another ConcreteState).

## Python example: TCP connection

```python
from abc import ABC, abstractmethod

class TCPConnection:
    """Context: holds current state and delegates."""
    def __init__(self):
        self._state: TCPState = ClosedState()

    def set_state(self, state: "TCPState") -> None:
        self._state = state

    def open(self) -> None:
        self._state.open(self)

    def close(self) -> None:
        self._state.close(self)

    def acknowledge(self) -> None:
        self._state.acknowledge(self)

class TCPState(ABC):
    @abstractmethod
    def open(self, connection: TCPConnection) -> None:
        pass

    @abstractmethod
    def close(self, connection: TCPConnection) -> None:
        pass

    @abstractmethod
    def acknowledge(self, connection: TCPConnection) -> None:
        pass

class ClosedState(TCPState):
    def open(self, connection: TCPConnection) -> None:
        print("Opening connection")
        connection.set_state(OpenState())

    def close(self, connection: TCPConnection) -> None:
        print("Already closed")

    def acknowledge(self, connection: TCPConnection) -> None:
        print("Cannot acknowledge when closed")

class OpenState(TCPState):
    def open(self, connection: TCPConnection) -> None:
        print("Already open")

    def close(self, connection: TCPConnection) -> None:
        print("Closing connection")
        connection.set_state(ClosedState())

    def acknowledge(self, connection: TCPConnection) -> None:
        print("ACK sent")


# Usage
conn = TCPConnection()
conn.open()        # Opening connection
conn.acknowledge() # ACK sent
conn.close()       # Closing connection
conn.acknowledge() # Cannot acknowledge when closed
```

## Python example: vending machine

```python
from abc import ABC, abstractmethod

class VendingMachine:
    def __init__(self):
        self._state: VendingState = IdleState()
        self._balance_cents = 0

    def set_state(self, state: "VendingState") -> None:
        self._state = state

    def insert_coin(self, cents: int) -> None:
        self._state.insert_coin(self, cents)

    def select_item(self, item_id: str) -> None:
        self._state.select_item(self, item_id)

    def cancel(self) -> None:
        self._state.cancel(self)

class VendingState(ABC):
    def insert_coin(self, machine: VendingMachine, cents: int) -> None:
        print("Invalid in current state")
    def select_item(self, machine: VendingMachine, item_id: str) -> None:
        print("Invalid in current state")
    def cancel(self, machine: VendingMachine) -> None:
        print("Invalid in current state")

class IdleState(VendingState):
    def insert_coin(self, machine: VendingMachine, cents: int) -> None:
        machine._balance_cents += cents
        machine.set_state(HasMoneyState())

class HasMoneyState(VendingState):
    def insert_coin(self, machine: VendingMachine, cents: int) -> None:
        machine._balance_cents += cents

    def select_item(self, machine: VendingMachine, item_id: str) -> None:
        if machine._balance_cents >= 100:
            machine._balance_cents -= 100
            print(f"Dispensing {item_id}")
            machine.set_state(IdleState())
        else:
            print("Insufficient funds")

    def cancel(self, machine: VendingMachine) -> None:
        print(f"Returning {machine._balance_cents} cents")
        machine._balance_cents = 0
        machine.set_state(IdleState())
```

## State vs Strategy

- **State**: Behavior depends on **internal** state that **changes** over time; state objects often trigger transitions.
- **Strategy**: Behavior is **chosen** by the client and typically **fixed** for the duration of use; no notion of “current state” changing from inside.

## Summary

| Pros | Cons |
|------|------|
| State-specific logic in one place per state | Many state classes if states are numerous |
| No big if/else on state variable | Context and states can hold references to each other |
| Easy to add new states and transitions | |

Use State when **behavior depends on internal state** and you want to **represent each state as a type** and delegate to it.
