"""SQLite database path and connection factory."""

import sqlite3
from pathlib import Path


def _database_path() -> Path:
    """Return the path to the SQLite database file."""
    base = Path(__file__).resolve().parent.parent.parent
    data_dir = base / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "agents.db"


def _create_tables(connection: sqlite3.Connection) -> None:
    """Create agents table if it does not exist."""
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS agents (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            provider TEXT NOT NULL,
            model TEXT NOT NULL,
            agent_md TEXT NOT NULL DEFAULT '',
            mcp_config TEXT NOT NULL DEFAULT '{}',
            ollama_base_url TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    connection.commit()
    _add_ollama_base_url_if_missing(connection)


def _add_ollama_base_url_if_missing(connection: sqlite3.Connection) -> None:
    """Add ollama_base_url column to existing agents table if missing."""
    cursor = connection.execute(
        "SELECT name FROM pragma_table_info('agents') WHERE name = 'ollama_base_url'"
    )
    if cursor.fetchone() is None:
        connection.execute(
            "ALTER TABLE agents ADD COLUMN ollama_base_url TEXT"
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
