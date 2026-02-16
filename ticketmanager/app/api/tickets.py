"""Ticket REST API routes."""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from ticketmanager.app.dependencies import get_ticket_service
from ticketmanager.app.models.ticket import (
    Ticket,
    TicketCreate,
    TicketStatus,
    TicketStatusUpdate,
    TicketUpdate,
)
from ticketmanager.app.services.ticket_service import TicketService

router = APIRouter()


@router.post("/tickets", response_model=Ticket)
def create_ticket(
    payload: TicketCreate,
    service: TicketService = Depends(get_ticket_service),
) -> Ticket:
    """Create a new ticket. Id and default start_datetime are set server-side."""
    if payload.status == TicketStatus.BLOCKED and not payload.blocked_by_id:
        raise HTTPException(
            status_code=400,
            detail="blocked_by_id is required when status is blocked",
        )
    try:
        return service.create(payload)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("/tickets", response_model=list[Ticket])
def list_tickets(
    service: TicketService = Depends(get_ticket_service),
    status: TicketStatus | None = Query(None, description="Filter by status"),
    assignee: str | None = Query(None, description="Filter by assignee"),
    from_date: datetime | None = Query(None, description="Tickets from this datetime (inclusive)"),
    to_date: datetime | None = Query(None, description="Tickets until this datetime (inclusive)"),
    search: str | None = Query(None, description="Search in title and instructions"),
) -> list[Ticket]:
    """List tickets with optional filters."""
    return service.list(
        status=status,
        assignee=assignee,
        from_date=from_date,
        to_date=to_date,
        search=search,
    )


@router.get("/tickets/{ticket_id}", response_model=Ticket)
def get_ticket(
    ticket_id: UUID,
    service: TicketService = Depends(get_ticket_service),
) -> Ticket:
    """Return a single ticket by id."""
    ticket = service.get_by_id(ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.put("/tickets/{ticket_id}", response_model=Ticket)
def update_ticket(
    ticket_id: UUID,
    payload: TicketUpdate,
    service: TicketService = Depends(get_ticket_service),
) -> Ticket:
    """Update a ticket. Only provided fields are updated."""
    ticket = service.update(ticket_id, payload)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.patch("/tickets/{ticket_id}/status", response_model=Ticket)
def update_ticket_status(
    ticket_id: UUID,
    payload: TicketStatusUpdate,
    service: TicketService = Depends(get_ticket_service),
) -> Ticket:
    """Update the status of a ticket. When status is blocked, blocked_by_ticket_id is required."""
    if payload.status == TicketStatus.BLOCKED:
        if payload.blocked_by_ticket_id is None:
            raise HTTPException(
                status_code=400,
                detail="blocked_by_ticket_id is required when status is blocked",
            )
        if payload.blocked_by_ticket_id == ticket_id:
            raise HTTPException(
                status_code=400,
                detail="A ticket cannot be blocked by itself",
            )
        blocker = service.get_by_id(payload.blocked_by_ticket_id)
        if blocker is None:
            raise HTTPException(
                status_code=400,
                detail="Blocking ticket not found",
            )
    ticket = service.update_status(ticket_id, payload)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.delete("/tickets/{ticket_id}", status_code=204)
def delete_ticket(
    ticket_id: UUID,
    service: TicketService = Depends(get_ticket_service),
) -> None:
    """Delete a ticket by id."""
    deleted = service.delete(ticket_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Ticket not found")
