# Mediator

Define an object that **encapsulates how a set of objects interact**. Promotes loose coupling by keeping objects from referring to each other explicitly; they communicate through the mediator.

## When to use

- Many objects communicate in complex, tangled ways (many-to-many); you want to centralize that logic.
- Reusing a component is hard because it depends on many others; you want to reduce dependencies.
- You want to change how objects interact without changing the objects themselves.

## Structure

- **Mediator**: Interface for communicating with colleagues. Often has methods like `notify(sender, event)` or specific methods for each kind of interaction.
- **ConcreteMediator**: Knows about all colleagues and implements coordination logic.
- **Colleague**: Each object that would otherwise talk to others; holds a reference to the mediator and notifies it (instead of calling other colleagues directly).

## Python example: chat room

Colleagues (users) send messages through the mediator (chat room); the mediator broadcasts to others.

```python
from abc import ABC, abstractmethod

class Mediator(ABC):
    @abstractmethod
    def notify(self, sender: "Colleague", event: str, payload: object = None) -> None:
        pass

class Colleague(ABC):
    def __init__(self, mediator: Mediator, name: str):
        self.mediator = mediator
        self.name = name

    @abstractmethod
    def receive(self, sender_name: str, message: str) -> None:
        pass

class ChatUser(Colleague):
    def send(self, message: str) -> None:
        self.mediator.notify(self, "message", message)

    def receive(self, sender_name: str, message: str) -> None:
        print(f"{self.name} received from {sender_name}: {message}")

class ChatRoom(Mediator):
    def __init__(self):
        self._users: list[ChatUser] = []

    def add_user(self, user: ChatUser) -> None:
        self._users.append(user)

    def notify(self, sender: Colleague, event: str, payload: object = None) -> None:
        if event == "message" and isinstance(sender, ChatUser) and isinstance(payload, str):
            for user in self._users:
                if user is not sender:
                    user.receive(sender.name, payload)


# Usage
room = ChatRoom()
alice = ChatUser(room, "Alice")
bob = ChatUser(room, "Bob")
room.add_user(alice)
room.add_user(bob)
alice.send("Hi Bob")  # Bob received from Alice: Hi Bob
```

## Python example: dialog (UI components)

Buttons, text fields, and lists don’t call each other; they notify the dialog mediator, which updates others.

```python
from abc import ABC, abstractmethod

class DialogMediator(ABC):
    @abstractmethod
    def on_button_clicked(self, button_id: str) -> None:
        pass

    @abstractmethod
    def on_text_changed(self, field_id: str, text: str) -> None:
        pass

class Button:
    def __init__(self, mediator: DialogMediator, id: str, label: str):
        self.mediator = mediator
        self.id = id
        self.label = label

    def click(self) -> None:
        self.mediator.on_button_clicked(self.id)

class TextField:
    def __init__(self, mediator: DialogMediator, id: str):
        self.mediator = mediator
        self.id = id
        self._text = ""

    def set_text(self, text: str) -> None:
        self._text = text
        self.mediator.on_text_changed(self.id, text)

class SearchDialog(DialogMediator):
    def __init__(self):
        self.search_field = TextField(self, "search")
        self.search_button = Button(self, "search_btn", "Search")
        self.results: list[str] = []

    def on_button_clicked(self, button_id: str) -> None:
        if button_id == "search_btn":
            query = self.search_field._text
            self.results = [f"Result for {query}"]
            print(self.results)

    def on_text_changed(self, field_id: str, text: str) -> None:
        if field_id == "search" and not text:
            self.results = []
```

## Mediator vs Observer

- **Observer**: One-to-many; subject notifies many observers. Observers don’t know about each other.
- **Mediator**: Many colleagues talk through one mediator. The mediator can orchestrate complex multi-way logic (e.g. “when A does X, tell B and C to do Y”).

## Summary

| Pros | Cons |
|------|------|
| Reduces coupling between colleagues | Mediator can become large and complex |
| Centralizes interaction logic | |
| Easy to add new colleagues (they only know the mediator) | |

Use Mediator when you have **many objects that need to coordinate** and you want to **avoid a web of direct references** between them.
