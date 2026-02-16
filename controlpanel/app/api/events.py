"""Events API: report and list platform events."""

from fastapi import APIRouter, Depends

from controlpanel.app.dependencies import get_event_store
from controlpanel.app.event_store import EventStore
from controlpanel.app.models.event import Event, EventReport

router = APIRouter(prefix="/api/events", tags=["events"])


@router.post("", status_code=201)
def report_event(
    report: EventReport,
    event_store: EventStore = Depends(get_event_store),
) -> dict[str, str]:
    """Accept an event from another service. Returns the created event id."""
    event = event_store.add(report)
    return {"id": str(event.id)}


@router.get("")
def list_events(
    limit: int = 100,
    event_store: EventStore = Depends(get_event_store),
) -> dict[str, list[Event]]:
    """Return recent events, newest first. Default limit 100."""
    events = event_store.list_events(limit=limit)
    return {"events": events}
