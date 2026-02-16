"""In-memory event store for platform events reported by services."""

from datetime import datetime
from uuid import uuid4

from controlpanel.app.models.event import Event, EventReport


class EventStore:
    """Bounded in-memory store of reported events. Newest first when listed."""

    def __init__(self, max_events: int = 500) -> None:
        self._max_events = max(1, max_events)
        self._events: list[Event] = []

    def add(self, report: EventReport) -> Event:
        """Append an event from a report; drop oldest if over capacity."""
        event = Event(
            id=uuid4(),
            timestamp=datetime.utcnow(),
            source=report.source,
            event=report.event,
            message=report.message,
        )
        self._events.append(event)
        while len(self._events) > self._max_events:
            self._events.pop(0)
        return event

    def list_events(self, limit: int = 100) -> list[Event]:
        """Return most recent events first, up to limit."""
        count = min(limit, len(self._events))
        if count <= 0:
            return []
        return list(reversed(self._events[-count:]))
