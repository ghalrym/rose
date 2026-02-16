"""Web UI routes: Kanban page and HTMX partials."""

from datetime import datetime
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from ticketmanager.app.dependencies import get_ticket_service
from ticketmanager.app.models.ticket import TicketCreate, TicketStatus, TicketStatusUpdate
from ticketmanager.app.services.ticket_service import TicketService

router = APIRouter()
templates_path = Path(__file__).resolve().parent / "templates"
templates = Jinja2Templates(directory=str(templates_path))


def _group_tickets_by_status(tickets: list) -> dict[str, list]:
    """Group tickets into status buckets for the Kanban columns."""
    groups: dict[str, list] = {
        "todo": [],
        "in_progress": [],
        "review": [],
        "done": [],
        "blocked": [],
    }
    for ticket in tickets:
        groups[ticket.status.value].append(ticket)
    return groups


@router.get("/", response_class=HTMLResponse)
def kanban_page(
    request: Request,
    service: TicketService = Depends(get_ticket_service),
    status: TicketStatus | None = None,
    assignee: str | None = None,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
    search: str | None = None,
    error: str | None = None,
) -> HTMLResponse:
    """Render the main Kanban board with optional filters."""
    tickets = service.list(
        status=status,
        assignee=assignee,
        from_date=from_date,
        to_date=to_date,
        search=search,
    )
    groups = _group_tickets_by_status(tickets)
    ticket_ids = {t.id for t in tickets}
    blocked_by_titles: dict[str, str] = {}
    for ticket in tickets:
        if ticket.blocked_by_id and ticket.blocked_by_id in ticket_ids:
            for other in tickets:
                if other.id == ticket.blocked_by_id:
                    blocked_by_titles[str(ticket.id)] = other.title
                    break
    return templates.TemplateResponse(
        request=request,
        name="kanban.html",
        context={
            "tickets_by_status": groups,
            "all_tickets": tickets,
            "blocked_by_titles": blocked_by_titles,
            "error": error or "",
            "filter_assignee": assignee or "",
            "filter_from_date": from_date.strftime("%Y-%m-%dT%H:%M") if from_date else "",
            "filter_to_date": to_date.strftime("%Y-%m-%dT%H:%M") if to_date else "",
            "filter_search": search or "",
        },
    )


@router.post("/tickets")
async def create_ticket_from_form(
    request: Request,
    service: TicketService = Depends(get_ticket_service),
) -> RedirectResponse:
    """Handle form submit to create a ticket; redirects to board."""
    form = await request.form()
    title = form.get("title", "").strip() or "Untitled"
    instructions = form.get("instructions", "").strip()
    assignee = form.get("assignee", "").strip()
    start_datetime_raw = form.get("start_datetime", "").strip()
    start_datetime: datetime | None = None
    if start_datetime_raw:
        start_datetime = datetime.fromisoformat(start_datetime_raw.replace("Z", "+00:00"))
    status_value = form.get("status", "todo").strip() or "todo"
    try:
        status = TicketStatus(status_value)
    except ValueError:
        status = TicketStatus.TODO
    blocked_by_raw = form.get("blocked_by_ticket_id", "").strip()
    blocked_by_id: UUID | None = None
    if blocked_by_raw:
        try:
            blocked_by_id = UUID(blocked_by_raw)
        except ValueError:
            blocked_by_id = None
    if status == TicketStatus.BLOCKED and not blocked_by_id:
        return RedirectResponse(url="/?error=create_blocked_requires_link", status_code=303)
    blocker = service.get_by_id(blocked_by_id) if blocked_by_id else None
    if status == TicketStatus.BLOCKED and blocked_by_id and blocker is None:
        return RedirectResponse(url="/?error=create_blocked_ticket_not_found", status_code=303)
    try:
        payload = TicketCreate(
            title=title,
            instructions=instructions,
            assignee=assignee,
            start_datetime=start_datetime,
            status=status,
            blocked_by_id=blocked_by_id if status == TicketStatus.BLOCKED else None,
        )
        service.create(payload)
    except ValueError:
        return RedirectResponse(url="/?error=create_invalid", status_code=303)
    return RedirectResponse(url="/", status_code=303)


@router.post("/tickets/{ticket_id}/status")
async def update_ticket_status_from_form(
    ticket_id: UUID,
    request: Request,
    service: TicketService = Depends(get_ticket_service),
) -> RedirectResponse:
    """Handle form submit to change ticket status; redirects to board."""
    form = await request.form()
    status_value = form.get("status", "").strip()
    if not status_value:
        return RedirectResponse(url="/", status_code=303)
    try:
        status = TicketStatus(status_value)
    except ValueError:
        return RedirectResponse(url="/", status_code=303)
    blocked_by_raw = form.get("blocked_by_ticket_id", "").strip()
    blocked_by_ticket_id: UUID | None = None
    if blocked_by_raw:
        try:
            blocked_by_ticket_id = UUID(blocked_by_raw)
        except ValueError:
            blocked_by_ticket_id = None
    if status == TicketStatus.BLOCKED and not blocked_by_ticket_id:
        return RedirectResponse(
            url="/?error=blocked_requires_link",
            status_code=303,
        )
    if status == TicketStatus.BLOCKED and blocked_by_ticket_id == ticket_id:
        return RedirectResponse(
            url="/?error=blocked_self",
            status_code=303,
        )
    if status == TicketStatus.BLOCKED and blocked_by_ticket_id:
        if service.get_by_id(blocked_by_ticket_id) is None:
            return RedirectResponse(
                url="/?error=blocked_ticket_not_found",
                status_code=303,
            )
    service.update_status(
        ticket_id,
        TicketStatusUpdate(status=status, blocked_by_ticket_id=blocked_by_ticket_id),
    )
    return RedirectResponse(url="/", status_code=303)
