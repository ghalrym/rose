"""SQLite database path and connection factory."""

import sqlite3
from pathlib import Path


def _database_path() -> Path:
    """Return the path to the SQLite database file."""
    base = Path(__file__).resolve().parent.parent.parent
    data_dir = base / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "tickets.db"


def _create_tables(connection: sqlite3.Connection) -> None:
    """Create tickets table if it does not exist and add blocked_by_id if missing."""
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS tickets (
            id TEXT PRIMARY KEY,
            start_datetime TEXT NOT NULL,
            assignee TEXT NOT NULL,
            title TEXT NOT NULL,
            instructions TEXT NOT NULL,
            status TEXT NOT NULL
        )
        """
    )
    connection.commit()
    _add_blocked_by_column_if_missing(connection)


def _add_blocked_by_column_if_missing(connection: sqlite3.Connection) -> None:
    """Add blocked_by_id column for existing databases."""
    cursor = connection.execute("PRAGMA table_info(tickets)")
    columns = [row[1] for row in cursor.fetchall()]
    if "blocked_by_id" not in columns:
        connection.execute("ALTER TABLE tickets ADD COLUMN blocked_by_id TEXT")
        connection.commit()


def get_connection() -> sqlite3.Connection:
    """Open a connection to the SQLite database and ensure schema exists.

    Returns:
        An open sqlite3.Connection. Caller must close it or use as context manager.

    Raises:
        sqlite3.Error: If the database cannot be opened or created.
    """
    path = _database_path()
    # Allow use from any thread: FastAPI runs sync deps in a thread pool but endpoints
    # run on the event-loop thread, so the same connection is used across threads.
    connection = sqlite3.connect(str(path), check_same_thread=False)
    connection.row_factory = sqlite3.Row
    _create_tables(connection)
    return connection
