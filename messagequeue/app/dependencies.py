"""FastAPI injectable dependencies for database, repository, and service."""

import sqlite3
from collections.abc import Generator

from fastapi import Depends

from messagequeue.app.persistence.database import get_connection
from messagequeue.app.persistence.session_repository import SessionRepository
from messagequeue.app.services.queue_service import QueueService


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


def get_session_repository(
    connection: sqlite3.Connection = Depends(get_db),
) -> SessionRepository:
    """Provide a SessionRepository for the request."""
    return SessionRepository(connection)


def get_queue_service(
    repository: SessionRepository = Depends(get_session_repository),
) -> QueueService:
    """Provide a QueueService for the request."""
    return QueueService(repository)
