"""SQLite-backed repository for agents."""

import json
import sqlite3
from datetime import datetime, timezone
from uuid import UUID

from agentmanager.app.models.agent import (
    Agent,
    AgentUpdate,
    McpServerConfig,
)


def _mcp_servers_to_json(mcp_servers: list[McpServerConfig]) -> str:
    """Serialize MCP server configs to JSON object for DB storage."""
    connection_dict: dict[str, dict] = {}
    for server in mcp_servers:
        entry: dict = {"transport": server.transport}
        if server.command is not None:
            entry["command"] = server.command
        if server.args is not None:
            entry["args"] = server.args
        if server.url is not None:
            entry["url"] = server.url
        if server.headers is not None:
            entry["headers"] = server.headers
        connection_dict[server.name] = entry
    return json.dumps(connection_dict)


class AgentRepository:
    """Persists and retrieves agents in SQLite."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        """Initialize with an open database connection.

        Args:
            connection: An open sqlite3.Connection (e.g. from get_connection).
        """
        self._connection = connection

    def create(self, agent: Agent) -> Agent:
        """Insert an agent into the database.

        Args:
            agent: The agent to insert (must have id and all fields set).

        Returns:
            The same Agent instance.

        Raises:
            sqlite3.IntegrityError: If id already exists.
        """
        now = datetime.now(timezone.utc).isoformat()
        self._connection.execute(
            """
            INSERT INTO agents (
                id, name, provider, model, agent_md, mcp_config,
                ollama_base_url, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(agent.id),
                agent.name,
                agent.provider.value,
                agent.model,
                agent.agent_md,
                _mcp_servers_to_json(agent.mcp_servers),
                agent.ollama_base_url,
                now,
                now,
            ),
        )
        self._connection.commit()
        return agent

    def get_by_id(self, agent_id: UUID) -> Agent | None:
        """Fetch an agent by id.

        Args:
            agent_id: The agent UUID.

        Returns:
            The Agent if found, otherwise None.
        """
        cursor = self._connection.execute(
            """
            SELECT id, name, provider, model, agent_md, mcp_config,
                   ollama_base_url, created_at, updated_at
            FROM agents WHERE id = ?
            """,
            (str(agent_id),),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return Agent.from_row(row)

    def list_all(self) -> list[Agent]:
        """List all agents ordered by created_at ascending."""
        cursor = self._connection.execute(
            """
            SELECT id, name, provider, model, agent_md, mcp_config,
                   ollama_base_url, created_at, updated_at
            FROM agents
            ORDER BY created_at ASC
            """
        )
        return [Agent.from_row(row) for row in cursor.fetchall()]

    def update(self, agent_id: UUID, payload: AgentUpdate) -> Agent | None:
        """Update an existing agent with the given fields.

        Args:
            agent_id: The agent to update.
            payload: Fields to update; only non-None fields are applied.

        Returns:
            The updated Agent if found, otherwise None.
        """
        existing = self.get_by_id(agent_id)
        if existing is None:
            return None
        updates: list[str] = []
        params: list[object] = []
        if payload.name is not None:
            updates.append("name = ?")
            params.append(payload.name)
        if payload.provider is not None:
            updates.append("provider = ?")
            params.append(payload.provider.value)
        if payload.model is not None:
            updates.append("model = ?")
            params.append(payload.model)
        if payload.agent_md is not None:
            updates.append("agent_md = ?")
            params.append(payload.agent_md)
        if payload.mcp_servers is not None:
            updates.append("mcp_config = ?")
            params.append(_mcp_servers_to_json(payload.mcp_servers))
        if payload.ollama_base_url is not None:
            updates.append("ollama_base_url = ?")
            value = payload.ollama_base_url.strip() or None
            params.append(value)
        if not updates:
            return existing
        updates.append("updated_at = ?")
        params.append(datetime.now(timezone.utc).isoformat())
        params.append(str(agent_id))
        self._connection.execute(
            f"UPDATE agents SET {', '.join(updates)} WHERE id = ?",
            params,
        )
        self._connection.commit()
        return self.get_by_id(agent_id)

    def delete(self, agent_id: UUID) -> bool:
        """Delete an agent by id.

        Args:
            agent_id: The agent to delete.

        Returns:
            True if a row was deleted, False if no such agent.
        """
        cursor = self._connection.execute(
            "DELETE FROM agents WHERE id = ?", (str(agent_id),)
        )
        self._connection.commit()
        return cursor.rowcount > 0
