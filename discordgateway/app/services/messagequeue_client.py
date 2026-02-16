"""HTTP client for the message queue API."""


class MessageQueueClient:
    """Facade for message queue REST calls (create session, send message, get history)."""

    def __init__(self, base_url: str, timeout: float = 60.0) -> None:
        """Initialize with message queue base URL.

        Args:
            base_url: Base URL for the message queue (e.g. http://messagequeue:8000).
            timeout: Request timeout in seconds.
        """
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    def create_session(
        self, participants: list[dict], session_id: str | None = None
    ) -> str:
        """Create a session (or return existing id if session_id provided and exists).

        Args:
            participants: List of {"name": str, "isAgent": bool} (exactly two).
            session_id: Optional stable session id.

        Returns:
            The session id.

        Raises:
            httpx.HTTPStatusError: If the request fails.
        """
        import httpx

        payload: dict = {"participants": participants}
        if session_id is not None:
            payload["sessionId"] = session_id
        response = httpx.post(
            f"{self._base_url}/api/sessions",
            json=payload,
            timeout=self._timeout,
        )
        response.raise_for_status()
        return response.json()["sessionId"]

    def send_message(self, session_id: str, user: str, message: str) -> None:
        """Append a message to a session.

        Raises:
            httpx.HTTPStatusError: If the session does not exist or request fails.
        """
        import httpx

        response = httpx.post(
            f"{self._base_url}/api/messages",
            json={"sessionId": session_id, "user": user, "message": message},
            timeout=self._timeout,
        )
        response.raise_for_status()

    def get_history(
        self, session_id: str, clear_unseen: bool = True
    ) -> tuple[list[dict], list[dict]]:
        """Return (participants, messages) for a session.

        Args:
            session_id: Session identifier.
            clear_unseen: If True, clear the unseen flag (default). If False, read-only.

        Returns:
            (participants, messages). Participants are [{"name": str, "isAgent": bool}].
            Messages are [{"user": str, "message": str}].

        Raises:
            httpx.HTTPStatusError: If session not found or request fails.
        """
        import httpx

        response = httpx.get(
            f"{self._base_url}/api/sessions/{session_id}/history",
            params={"clear_unseen": str(clear_unseen).lower()},
            timeout=self._timeout,
        )
        response.raise_for_status()
        data = response.json()
        participants = data.get("participants", [])
        messages = [
            {"user": entry["user"], "message": entry["message"]}
            for entry in data.get("messages", [])
        ]
        return participants, messages
