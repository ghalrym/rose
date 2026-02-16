# Observer

Define a **one-to-many dependency** so that when one object (subject) changes state, all its dependents (observers) are notified and updated automatically.

## When to use

- A change to one object needs to be reflected in others without knowing how many or who they are (loose coupling).
- You need to broadcast events (e.g. “model changed”, “user logged in”) to multiple subscribers.

## Structure

- **Subject**: Holds a list of observers; provides attach/detach; notifies all observers when state changes.
- **Observer**: Interface with an update method (or callback) that the subject calls.
- **ConcreteSubject**: The object whose state changes; notifies observers.
- **ConcreteObserver**: Reacts to the notification (e.g. refresh UI, log, send event).

## Python example: subject and observers

```python
from abc import ABC, abstractmethod

class Observer(ABC):
    @abstractmethod
    def update(self, subject: "Subject", event: object = None) -> None:
        pass

class Subject(ABC):
    def __init__(self):
        self._observers: list[Observer] = []

    def attach(self, observer: Observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, event: object = None) -> None:
        for obs in self._observers:
            obs.update(self, event)

class DataModel(Subject):
    def __init__(self):
        super().__init__()
        self._value = 0

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, v: int) -> None:
        if self._value != v:
            self._value = v
            self.notify(event={"field": "value", "new": v})

class LoggingObserver(Observer):
    def update(self, subject: Subject, event: object = None) -> None:
        print(f"Log: subject changed, event={event}")

class UIObserver(Observer):
    def update(self, subject: Subject, event: object = None) -> None:
        if isinstance(subject, DataModel):
            print(f"UI: refresh with value={subject.value}")


# Usage
model = DataModel()
model.attach(LoggingObserver())
model.attach(UIObserver())
model.value = 42  # Log: ... ; UI: refresh with value=42
```

## Python example: event bus (many subjects, many observers)

```python
from typing import Callable, Any

class EventBus:
    def __init__(self):
        self._handlers: dict[str, list[Callable[..., None]]] = {}

    def subscribe(self, event_type: str, handler: Callable[..., None]) -> None:
        self._handlers.setdefault(event_type, []).append(handler)

    def unsubscribe(self, event_type: str, handler: Callable[..., None]) -> None:
        if event_type in self._handlers:
            self._handlers[event_type].remove(handler)

    def publish(self, event_type: str, **payload: Any) -> None:
        for handler in self._handlers.get(event_type, []):
            handler(**payload)

# Usage
bus = EventBus()
bus.subscribe("user.login", lambda user_id: print(f"Audit: login {user_id}"))
bus.subscribe("user.login", lambda user_id: print(f"Analytics: login {user_id}"))
bus.publish("user.login", user_id=123)
```

## Python: using `property` and callbacks

For a single object with a few observers, you can notify inside a property setter:

```python
class ObservableValue:
    def __init__(self, value: int = 0):
        self._value = value
        self._listeners: list[Callable[[int], None]] = []

    def subscribe(self, listener: Callable[[int], None]) -> None:
        self._listeners.append(listener)

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, v: int) -> None:
        self._value = v
        for fn in self._listeners:
            fn(v)
```

## Summary

| Pros | Cons |
|------|------|
| Loose coupling between subject and observers | Can cause cascading updates and performance cost |
| Broadcast changes to unknown number of observers | |
| Easy to add/remove observers at runtime | |

Use Observer (or an event bus) when **one source of change** must **notify many subscribers** without the source knowing who they are. In distributed systems, this is often done with a message queue (e.g. Redis Pub/Sub) instead of in-process observers.
