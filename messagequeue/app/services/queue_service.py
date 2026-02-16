"""Application service for message queue operations."""

import json
from uuid import uuid4

from messagequeue.app.models.message import (
    HistoryEntry,
    Participant,
)
from messagequeue.app.persistence.session_repository import SessionRepository


class SessionNotFoundError(Exception):
    """Raised when a session does not exist."""


class QueueService:
    """Orchestrates send, poll, and history operations."""

    def __init__(self, repository: SessionRepository) -> None:
        """Initialize with a session repository.

        Args:
            repository: The repository used for persistence.
        """
        self._repository = repository

    def create_session(
        self, participants: list[Participant], session_id: str | None = None
    ) -> tuple[str, bool]:
        """Create a session with exactly two participants, or return existing id if provided.

        Args:
            participants: The two participants (name, isAgent).
            session_id: Optional. If provided and a session with this id exists, return it
                without creating (idempotent). Otherwise create with this id or a new UUID.

        Returns:
            (session_id, created): The session id and True if created, False if existing.
        """
        if session_id is not None and self._repository.session_exists(session_id):
            return session_id, False
        resolved_id = session_id if session_id is not None else str(uuid4())
        participants_json = json.dumps(
            [{"name": p.name, "isAgent": p.isAgent} for p in participants]
        )
        self._repository.create_session(resolved_id, participants_json)
        return resolved_id, True

    def send_message(self, session_id: str, user: str, message: str) -> None:
        """Append a message to the session and mark it as having unseen content.

        Raises:
            SessionNotFoundError: If the session does not exist.
        """
        if not self._repository.append_message(session_id, user, message):
            raise SessionNotFoundError(f"Session not found: {session_id}")

    def has_unseen(self, session_id: str) -> bool:
        """Return whether the session has an unseen message."""
        return self._repository.get_has_unseen(session_id)

    def get_history(
        self, session_id: str, clear_unseen: bool = True
    ) -> tuple[list[Participant], list[HistoryEntry]]:
        """Return full conversation history (participants + messages).

        Optionally clear the unseen flag so subsequent poll/updated checks do not
        see this session until a new message is added.

        Args:
            session_id: Session identifier.
            clear_unseen: If True, clear the unseen flag after reading (default).
                If False, return history without clearing (read-only).

        Returns:
            (participants, messages). Participants are the two {name, isAgent} from session creation.

        Raises:
            SessionNotFoundError: If the session does not exist.
        """
        participants_json = self._repository.get_participants_json(session_id)
        if participants_json is None:
            raise SessionNotFoundError(f"Session not found: {session_id}")
        participants_data = json.loads(participants_json)
        participants = [
            Participant(name=p["name"], isAgent=p["isAgent"])
            for p in participants_data
        ]
        if clear_unseen:
            pairs = self._repository.get_messages_and_clear_unseen(session_id)
        else:
            pairs = self._repository.get_messages(session_id)
        messages = [HistoryEntry(user=u, message=m) for u, m in pairs]
        return participants, messages

    def list_sessions_with_updates(self) -> list[str]:
        """Return session ids that have an unseen update."""
        return self._repository.list_session_ids_with_updates()

    def find_session_by_participants(self, participants: list[Participant]) -> str | None:
        """Return the session id for a chat between the two given participants, or None.

        Matching is order-independent: [A, B] matches [B, A].
        """
        if len(participants) != 2:
            return None
        wanted = frozenset((p.name, p.isAgent) for p in participants)
        for session_id, participants_json in self._repository.list_all_sessions_with_participants():
            try:
                data = json.loads(participants_json)
                if len(data) != 2:
                    continue
                session_set = frozenset((p["name"], p["isAgent"]) for p in data)
                if session_set == wanted:
                    return session_id
            except (json.JSONDecodeError, KeyError, TypeError):
                continue
        return None
