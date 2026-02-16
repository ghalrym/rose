"""SQLite database path and connection factory."""

import sqlite3
from pathlib import Path


def _database_path() -> Path:
    """Return the path to the SQLite database file."""
    base = Path(__file__).resolve().parent.parent.parent
    data_dir = base / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "gateway.db"


def _create_tables(connection: sqlite3.Connection) -> None:
    """Create config and channel_assignments tables if they do not exist."""
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL DEFAULT ''
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS channel_assignments (
            guild_id TEXT NOT NULL,
            channel_id TEXT NOT NULL,
            agent_id TEXT NOT NULL,
            PRIMARY KEY (guild_id, channel_id)
        )
        """
    )
    connection.commit()


def get_connection() -> sqlite3.Connection:
    """Open a connection to the SQLite database and ensure schema exists.

    Returns:
        An open sqlite3.Connection. Caller must close it or use as context manager.

    Raises:
        sqlite3.Error: If the database cannot be opened or created.
    """
    path = _database_path()
    connection = sqlite3.connect(str(path), check_same_thread=False)
    connection.row_factory = sqlite3.Row
    _create_tables(connection)
    return connection
