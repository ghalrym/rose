"""FastAPI injectable dependencies for database, repositories, services, and clients."""

import sqlite3
from collections.abc import Generator

from fastapi import Depends

from discordgateway.app.config import GatewayConfig
from discordgateway.app.persistence.channel_assignment_repository import (
    ChannelAssignmentRepository,
)
from discordgateway.app.persistence.config_repository import ConfigRepository
from discordgateway.app.persistence.database import get_connection
from discordgateway.app.services.agentmanager_client import AgentmanagerClient
from discordgateway.app.services.config_service import ConfigService
from discordgateway.app.services.messagequeue_client import MessageQueueClient


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


def get_config_repository(
    connection: sqlite3.Connection = Depends(get_db),
) -> ConfigRepository:
    """Provide a ConfigRepository for the request."""
    return ConfigRepository(connection)


def get_channel_assignment_repository(
    connection: sqlite3.Connection = Depends(get_db),
) -> ChannelAssignmentRepository:
    """Provide a ChannelAssignmentRepository for the request."""
    return ChannelAssignmentRepository(connection)


def get_config_service(
    config_repository: ConfigRepository = Depends(get_config_repository),
    channel_assignment_repository: ChannelAssignmentRepository = Depends(
        get_channel_assignment_repository
    ),
) -> ConfigService:
    """Provide a ConfigService for the request."""
    return ConfigService(config_repository, channel_assignment_repository)


def get_gateway_config() -> GatewayConfig:
    """Provide gateway config (from env)."""
    return GatewayConfig()


def get_messagequeue_client(
    config: GatewayConfig = Depends(get_gateway_config),
) -> MessageQueueClient:
    """Provide a MessageQueueClient for the request."""
    return MessageQueueClient(config.messagequeue_url)


def get_agentmanager_client(
    config: GatewayConfig = Depends(get_gateway_config),
) -> AgentmanagerClient:
    """Provide an AgentmanagerClient for the request."""
    return AgentmanagerClient(config.agentmanager_url)
