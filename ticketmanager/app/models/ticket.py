"""Ticket domain and API models."""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class TicketStatus(str, Enum):
    """Workflow status for a ticket."""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"
    BLOCKED = "blocked"


class Ticket(BaseModel):
    """A single ticket with id, timestamps, assignee, status, and optional block link."""

    id: UUID
    start_datetime: datetime
    assignee: str
    title: str
    instructions: str
    status: TicketStatus
    blocked_by_id: UUID | None = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_row(cls, row: object) -> "Ticket":
        """Build a Ticket from a database row (e.g. sqlite3.Row).

        Args:
            row: Row with keys id, start_datetime, assignee, title, instructions, status,
                and optionally blocked_by_id.

        Returns:
            A Ticket instance.

        Raises:
            KeyError: If a required key is missing from the row.
            ValueError: If id or start_datetime cannot be parsed.
        """
        data = dict(row)
        blocked_by_id_raw = data.get("blocked_by_id")
        blocked_by_id = UUID(str(blocked_by_id_raw)) if blocked_by_id_raw else None
        return cls(
            id=UUID(str(data["id"])),
            start_datetime=datetime.fromisoformat(str(data["start_datetime"])),
            assignee=str(data["assignee"]),
            title=str(data["title"]),
            instructions=str(data["instructions"]),
            status=TicketStatus(str(data["status"])),
            blocked_by_id=blocked_by_id,
        )


class TicketCreate(BaseModel):
    """Payload for creating a new ticket. Id is generated server-side."""

    title: str
    instructions: str = ""
    assignee: str = ""
    start_datetime: datetime | None = None
    status: TicketStatus = TicketStatus.TODO
    blocked_by_id: UUID | None = None

    model_config = {"from_attributes": True}


class TicketUpdate(BaseModel):
    """Payload for updating a ticket. All fields optional."""

    title: str | None = None
    instructions: str | None = None
    assignee: str | None = None
    start_datetime: datetime | None = None
    blocked_by_id: UUID | None = None

    model_config = {"from_attributes": True}


class TicketStatusUpdate(BaseModel):
    """Change ticket status. When status is blocked, blocked_by_ticket_id is required."""

    status: TicketStatus = Field(..., description="New status")
    blocked_by_ticket_id: UUID | None = Field(
        None,
        description="Required when status is blocked: id of the ticket that blocks this one.",
    )

    model_config = {"from_attributes": True}
