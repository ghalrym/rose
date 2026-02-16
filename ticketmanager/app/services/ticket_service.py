"""Application service for ticket operations."""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from ticketmanager.app.models.ticket import (
    Ticket,
    TicketCreate,
    TicketStatus,
    TicketStatusUpdate,
    TicketUpdate,
)
from ticketmanager.app.persistence.ticket_repository import TicketRepository


class TicketService:
    """Orchestrates ticket creation, updates, and queries."""

    def __init__(self, repository: TicketRepository) -> None:
        """Initialize with a ticket repository.

        Args:
            repository: The repository used for persistence.
        """
        self._repository = repository

    def create(self, payload: TicketCreate) -> Ticket:
        """Create a ticket. When status is BLOCKED, blocked_by_id must reference an existing ticket.

        Args:
            payload: Creation payload including optional status and blocked_by_id.

        Returns:
            The created Ticket.

        Raises:
            ValueError: When status is BLOCKED but blocked_by_id is missing or invalid.
            sqlite3.IntegrityError: If a duplicate id is generated (extremely unlikely).
        """
        if payload.status == TicketStatus.BLOCKED:
            if payload.blocked_by_id is None:
                raise ValueError("blocked_by_id is required when status is blocked")
            if self._repository.get_by_id(payload.blocked_by_id) is None:
                raise ValueError("Blocking ticket not found")
        ticket_id = uuid4()
        start_datetime = payload.start_datetime or datetime.now(timezone.utc)
        ticket = Ticket(
            id=ticket_id,
            start_datetime=start_datetime,
            assignee=payload.assignee,
            title=payload.title,
            instructions=payload.instructions,
            status=payload.status,
            blocked_by_id=payload.blocked_by_id if payload.status == TicketStatus.BLOCKED else None,
        )
        return self._repository.create(ticket)

    def get_by_id(self, ticket_id: UUID) -> Ticket | None:
        """Return a ticket by id, or None if not found."""
        return self._repository.get_by_id(ticket_id)

    def list(
        self,
        status: TicketStatus | None = None,
        assignee: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        search: str | None = None,
    ) -> list[Ticket]:
        """List tickets with optional filters."""
        return self._repository.list(
            status=status,
            assignee=assignee or None,
            from_date=from_date,
            to_date=to_date,
            search=search or None,
        )

    def update(self, ticket_id: UUID, payload: TicketUpdate) -> Ticket | None:
        """Update a ticket by id. Returns None if the ticket does not exist."""
        return self._repository.update(ticket_id, payload)

    def update_status(self, ticket_id: UUID, payload: TicketStatusUpdate) -> Ticket | None:
        """Update status. When BLOCKED, blocked_by_ticket_id must reference another ticket."""
        blocked_by_id = (
            payload.blocked_by_ticket_id
            if payload.status == TicketStatus.BLOCKED
            else None
        )
        return self._repository.update_status(
            ticket_id,
            payload.status,
            blocked_by_id=blocked_by_id,
        )

    def delete(self, ticket_id: UUID) -> bool:
        """Delete a ticket by id. Returns True if deleted, False if not found."""
        return self._repository.delete(ticket_id)
