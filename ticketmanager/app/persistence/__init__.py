"""Persistence layer: database and repositories."""

from ticketmanager.app.persistence.database import get_connection
from ticketmanager.app.persistence.ticket_repository import TicketRepository

__all__ = [
    "get_connection",
    "TicketRepository",
]
