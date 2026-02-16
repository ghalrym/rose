"""Repository for channel-to-agent assignments."""

import sqlite3


class ChannelAssignmentRepository:
    """Persists and retrieves (guild_id, channel_id) -> agent_id assignments."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        """Initialize with an open database connection.

        Args:
            connection: An open sqlite3.Connection (e.g. from get_connection).
        """
        self._connection = connection

    def list_all(self) -> list[tuple[str, str, str]]:
        """Return all assignments as (guild_id, channel_id, agent_id) tuples."""
        cursor = self._connection.execute(
            "SELECT guild_id, channel_id, agent_id FROM channel_assignments ORDER BY guild_id, channel_id"
        )
        return [(row["guild_id"], row["channel_id"], row["agent_id"]) for row in cursor.fetchall()]

    def get_agent_id(self, guild_id: str, channel_id: str) -> str | None:
        """Return the agent_id for the given guild and channel, or None if not assigned."""
        cursor = self._connection.execute(
            "SELECT agent_id FROM channel_assignments WHERE guild_id = ? AND channel_id = ?",
            (guild_id, channel_id),
        )
        row = cursor.fetchone()
        return row["agent_id"] if row is not None else None

    def upsert(self, guild_id: str, channel_id: str, agent_id: str) -> None:
        """Create or update the assignment for this guild and channel."""
        self._connection.execute(
            """INSERT INTO channel_assignments (guild_id, channel_id, agent_id)
               VALUES (?, ?, ?)
               ON CONFLICT (guild_id, channel_id) DO UPDATE SET agent_id = ?""",
            (guild_id, channel_id, agent_id, agent_id),
        )
        self._connection.commit()

    def delete(self, guild_id: str, channel_id: str) -> bool:
        """Remove the assignment for this guild and channel. Return True if a row was deleted."""
        cursor = self._connection.execute(
            "DELETE FROM channel_assignments WHERE guild_id = ? AND channel_id = ?",
            (guild_id, channel_id),
        )
        self._connection.commit()
        return cursor.rowcount > 0
