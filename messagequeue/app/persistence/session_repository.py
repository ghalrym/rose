"""SQLite-backed repository for sessions and messages."""

import json
import sqlite3


class SessionRepository:
    """Persists and retrieves sessions and messages in SQLite."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        """Initialize with an open database connection.

        Args:
            connection: An open sqlite3.Connection (e.g. from get_connection).
        """
        self._connection = connection

    def create_session(self, session_id: str, participants_json: str) -> None:
        """Create a session with the given id and participants. Fails if id exists."""
        self._connection.execute(
            "INSERT INTO sessions (id, has_unseen, participants) VALUES (?, 0, ?)",
            (session_id, participants_json),
        )
        self._connection.commit()

    def session_exists(self, session_id: str) -> bool:
        """Return True if the session exists."""
        cursor = self._connection.execute(
            "SELECT 1 FROM sessions WHERE id = ?", (session_id,)
        )
        return cursor.fetchone() is not None

    def get_participants_json(self, session_id: str) -> str | None:
        """Return the participants JSON for the session, or None if not found."""
        cursor = self._connection.execute(
            "SELECT participants FROM sessions WHERE id = ?", (session_id,)
        )
        row = cursor.fetchone()
        return row["participants"] if row is not None else None

    def append_message(self, session_id: str, user: str, message: str) -> bool:
        """Append a message to a session and set has_unseen to 1.

        Args:
            session_id: Session identifier.
            user: Sender identifier.
            message: Message content.

        Returns:
            True if the message was appended, False if the session does not exist.
        """
        if not self.session_exists(session_id):
            return False
        cursor = self._connection.execute(
            "SELECT COALESCE(MAX(ordinal), 0) + 1 FROM messages WHERE session_id = ?",
            (session_id,),
        )
        ordinal = cursor.fetchone()[0]
        self._connection.execute(
            "INSERT INTO messages (session_id, user, message, ordinal) VALUES (?, ?, ?, ?)",
            (session_id, user, message, ordinal),
        )
        self._connection.execute(
            "UPDATE sessions SET has_unseen = 1 WHERE id = ?", (session_id,)
        )
        self._connection.commit()
        return True

    def get_has_unseen(self, session_id: str) -> bool:
        """Return whether the session has an unseen message."""
        cursor = self._connection.execute(
            "SELECT has_unseen FROM sessions WHERE id = ?",
            (session_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return False
        return bool(row["has_unseen"])

    def clear_has_unseen(self, session_id: str) -> None:
        """Set has_unseen to 0 for the session."""
        self._connection.execute(
            "UPDATE sessions SET has_unseen = 0 WHERE id = ?",
            (session_id,),
        )
        self._connection.commit()

    def get_messages(self, session_id: str) -> list[tuple[str, str]]:
        """Return (user, message) pairs for the session in chronological order."""
        cursor = self._connection.execute(
            """
            SELECT user, message FROM messages
            WHERE session_id = ?
            ORDER BY ordinal ASC
            """,
            (session_id,),
        )
        return [(row["user"], row["message"]) for row in cursor.fetchall()]

    def get_messages_and_clear_unseen(self, session_id: str) -> list[tuple[str, str]]:
        """Return messages for the session and set has_unseen to 0."""
        messages = self.get_messages(session_id)
        self.clear_has_unseen(session_id)
        return messages

    def list_session_ids_with_updates(self) -> list[str]:
        """Return session ids that have has_unseen = 1."""
        cursor = self._connection.execute(
            "SELECT id FROM sessions WHERE has_unseen = 1 ORDER BY id ASC",
            (),
        )
        return [row["id"] for row in cursor.fetchall()]

    def list_all_sessions_with_participants(self) -> list[tuple[str, str]]:
        """Return (session_id, participants_json) for all sessions."""
        cursor = self._connection.execute(
            "SELECT id, participants FROM sessions ORDER BY id ASC",
            (),
        )
        return [(row["id"], row["participants"]) for row in cursor.fetchall()]
