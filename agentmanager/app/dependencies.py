"""FastAPI injectable dependencies for database, repository, and services."""

import sqlite3
from collections.abc import Generator

from fastapi import Depends

from agentmanager.app.persistence.agent_repository import AgentRepository
from agentmanager.app.persistence.database import get_connection
from agentmanager.app.services.agent_service import AgentService
from agentmanager.app.services.chat_service import ChatService


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


def get_agent_repository(
    connection: sqlite3.Connection = Depends(get_db),
) -> AgentRepository:
    """Provide an AgentRepository for the request."""
    return AgentRepository(connection)


def get_agent_service(
    repository: AgentRepository = Depends(get_agent_repository),
) -> AgentService:
    """Provide an AgentService for the request."""
    return AgentService(repository)


def get_chat_service(
    repository: AgentRepository = Depends(get_agent_repository),
) -> ChatService:
    """Provide a ChatService for the request."""
    return ChatService(repository)
