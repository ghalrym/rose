"""Repository for gateway config (e.g. Discord bot token)."""

import sqlite3

CONFIG_KEY_TOKEN = "discord_bot_token"


class ConfigRepository:
    """Persists and retrieves gateway config in SQLite."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        """Initialize with an open database connection.

        Args:
            connection: An open sqlite3.Connection (e.g. from get_connection).
        """
        self._connection = connection

    def get_token(self) -> str | None:
        """Return the stored Discord bot token, or None if not set.

        Returns:
            The raw token string, or None if no token is stored.
        """
        cursor = self._connection.execute(
            "SELECT value FROM config WHERE key = ?", (CONFIG_KEY_TOKEN,)
        )
        row = cursor.fetchone()
        if row is None:
            return None
        value = row["value"]
        return value if value else None

    def set_token(self, token: str | None) -> None:
        """Store or clear the Discord bot token.

        Args:
            token: The token to store, or None to clear.
        """
        value = token if token else ""
        self._connection.execute(
            "INSERT INTO config (key, value) VALUES (?, ?) ON CONFLICT (key) DO UPDATE SET value = ?",
            (CONFIG_KEY_TOKEN, value, value),
        )
        self._connection.commit()

    def get_token_preview(self) -> str | None:
        """Return the last four characters of the token for display, or None if not set."""
        token = self.get_token()
        if not token or len(token) < 4:
            return None
        return token[-4:]
