"""FastAPI injectable dependencies for database, repository, and service."""

import sqlite3
from collections.abc import Generator

from fastapi import Depends
from ticketmanager.app.persistence.database import get_connection
from ticketmanager.app.persistence.ticket_repository import TicketRepository
from ticketmanager.app.services.ticket_service import TicketService


def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Provide a database connection for the request and close it when done.

    Yields:
        An open sqlite3.Connection.

    Raises:
        sqlite3.Error: If the database cannot be opened.
    """
    connection = get_connection()
    try:
        yield connection
    finally:
        connection.close()


def get_ticket_repository(
    connection: sqlite3.Connection = Depends(get_db),
) -> TicketRepository:
    """Provide a TicketRepository for the request."""
    return TicketRepository(connection)


def get_ticket_service(
    repository: TicketRepository = Depends(get_ticket_repository),
) -> TicketService:
    """Provide a TicketService for the request."""
    return TicketService(repository)
