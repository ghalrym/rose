# Command

Encapsulate a **request as an object**, so you can parameterize clients with different requests, queue or log requests, and support undo.

## When to use

- You want to **queue** operations (e.g. job queue, async processing) or **log** them for replay/audit.
- You need **undo/redo** (store commands and reverse them).
- You want to **decouple** the invoker (button, scheduler) from the code that does the work (receiver).
- You want to support **transactions** (run several commands; roll back if one fails).

## Structure

- **Command**: Abstract interface with an `execute()` method (and optionally `undo()`).
- **ConcreteCommand**: Holds a reference to the **Receiver** and parameters; implements `execute()` by calling the receiver.
- **Invoker**: Holds a command and calls `execute()` (e.g. button, menu, queue consumer).
- **Receiver**: The object that does the actual work (optional; the command can do the work itself).

## Python example: undoable operations

```python
from abc import ABC, abstractmethod

class Command(ABC):
    @abstractmethod
    def execute(self) -> None:
        pass

    @abstractmethod
    def undo(self) -> None:
        pass

class Light:
    """Receiver."""
    def __init__(self):
        self.on = False

    def turn_on(self) -> None:
        self.on = True
        print("Light on")

    def turn_off(self) -> None:
        self.on = False
        print("Light off")

class LightOnCommand(Command):
    def __init__(self, light: Light):
        self.light = light

    def execute(self) -> None:
        self.light.turn_on()

    def undo(self) -> None:
        self.light.turn_off()

class LightOffCommand(Command):
    def __init__(self, light: Light):
        self.light = light

    def execute(self) -> None:
        self.light.turn_off()

    def undo(self) -> None:
        self.light.turn_on()


class RemoteControl:
    """Invoker: holds command and optional undo stack."""
    def __init__(self):
        self._command: Command | None = None
        self._undo_stack: list[Command] = []

    def set_command(self, command: Command) -> None:
        self._command = command

    def press_button(self) -> None:
        if self._command:
            self._command.execute()
            self._undo_stack.append(self._command)

    def press_undo(self) -> None:
        if self._undo_stack:
            cmd = self._undo_stack.pop()
            cmd.undo()


# Usage
light = Light()
remote = RemoteControl()
remote.set_command(LightOnCommand(light))
remote.press_button()   # Light on
remote.press_undo()     # Light off
```

## Python example: job queue (commands as objects)

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
import json

class Job(ABC):
    """Command that can be serialized and run later."""
    @abstractmethod
    def execute(self) -> Any:
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict) -> "Job":
        pass

@dataclass
class SendEmailJob(Job):
    to: str
    subject: str
    body: str

    def execute(self) -> Any:
        print(f"Sending to {self.to}: {self.subject}")
        return "sent"

    def to_dict(self) -> dict:
        return {"type": "SendEmailJob", "to": self.to, "subject": self.subject, "body": self.body}

    @classmethod
    def from_dict(cls, data: dict) -> "SendEmailJob":
        return cls(to=data["to"], subject=data["subject"], body=data["body"])

# Queue: serialize command, push; worker deserializes and executes
def enqueue(job: Job) -> None:
    payload = json.dumps(job.to_dict())
    print(f"Enqueued: {payload}")

def process(payload: str) -> Any:
    data = json.loads(payload)
    job_type = data.pop("type")
    if job_type == "SendEmailJob":
        job = SendEmailJob.from_dict(data)
    else:
        raise ValueError(job_type)
    return job.execute()

job = SendEmailJob("user@example.com", "Hi", "Hello")
enqueue(job)
process(json.dumps(job.to_dict()))
```

## Python example: simple callable command

When you don’t need undo or serialization, a callable is enough:

```python
from typing import Callable

def make_command(receiver: object, method_name: str, *args, **kwargs) -> Callable[[], None]:
    def execute():
        getattr(receiver, method_name)(*args, **kwargs)
    return execute

class Printer:
    def print_msg(self, msg: str):
        print(msg)

p = Printer()
cmd = make_command(p, "print_msg", "Hello")
cmd()
```

## Summary

| Pros | Cons |
|------|------|
| Decouple invoker from receiver | Extra class per command type |
| Queue, log, undo/redo, transactions | |
| Easy to add new commands | |

Use Command when you need **queueable**, **loggable**, or **undoable** operations, or when you want to **decouple** who triggers an action from who performs it.
