"""Web UI routes: control panel index, events page, and iframe."""

from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from controlpanel.app.config import ServiceUrls
from controlpanel.app.dependencies import get_event_store, get_service_urls
from controlpanel.app.event_store import EventStore

router = APIRouter()
templates_path = Path(__file__).resolve().parent / "templates"
templates = Jinja2Templates(directory=str(templates_path))


@router.get("/", response_class=HTMLResponse)
def index(
    request: Request,
    service_urls: ServiceUrls = Depends(get_service_urls),
) -> HTMLResponse:
    """Render the control panel: nav links and iframe for the selected service."""
    context = {"request": request, **service_urls.as_context()}
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=context,
    )


@router.get("/events", response_class=HTMLResponse)
def events_page(
    request: Request,
    event_store: EventStore = Depends(get_event_store),
) -> HTMLResponse:
    """Render the events list page (vertical list with time)."""
    events = event_store.list_events(limit=200)
    return templates.TemplateResponse(
        request=request,
        name="events.html",
        context={"request": request, "events": events},
    )
