"""Event models for reporting and displaying platform events."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class EventReport(BaseModel):
    """Payload for POST /api/events: another service reports an event."""

    source: str = Field(..., description="Service name, e.g. ticketmanager, agentmanager")
    event: str = Field(..., description="Event type, e.g. ticket.created")
    message: str | None = Field(None, description="Optional human-readable detail")


class Event(BaseModel):
    """Stored event with id and timestamp."""

    id: UUID
    timestamp: datetime
    source: str
    event: str
    message: str | None = None
