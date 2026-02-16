"""FastAPI dependencies for the control panel."""

from controlpanel.app.config import ServiceUrls
from controlpanel.app.event_store import EventStore

_service_urls: ServiceUrls | None = None
_event_store: EventStore | None = None


def get_service_urls() -> ServiceUrls:
    """Return the singleton ServiceUrls instance."""
    global _service_urls
    if _service_urls is None:
        _service_urls = ServiceUrls()
    return _service_urls


def get_event_store() -> EventStore:
    """Return the singleton EventStore instance."""
    global _event_store
    if _event_store is None:
        _event_store = EventStore(max_events=500)
    return _event_store
