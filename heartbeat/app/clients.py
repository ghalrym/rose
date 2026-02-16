"""HTTP clients for agentmanager, messagequeue, and ticketmanager APIs."""

import logging
from uuid import UUID

import httpx

from heartbeat.app.config import HEARTBEAT_IS_AGENT, HEARTBEAT_USER, HeartbeatConfig

logger = logging.getLogger(__name__)


class ServiceClient:
    """Facade for REST calls to agentmanager, message queue, and ticketmanager."""

    def __init__(self, config: HeartbeatConfig) -> None:
        """Initialize with base URLs from config.

        Args:
            config: Heartbeat configuration with service URLs.
        """
        self._config = config
        self._timeout = 60.0

    def list_sessions_with_updates(self) -> list[str]:
        """Return session ids that have an unseen update."""
        response = httpx.get(
            f"{self._config.messagequeue_url}/api/sessions/updated",
            timeout=self._timeout,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("session_ids", [])

    def get_session_history(
        self, session_id: str
    ) -> tuple[list[dict], list[dict]]:
        """Return (participants, messages) for a session. Clears unseen flag.

        Returns:
            (participants, messages). Participants are [{"name": str, "isAgent": bool}].
            Messages are [{"user": str, "message": str}].

        Raises:
            httpx.HTTPStatusError: If session not found or request fails.
        """
        response = httpx.get(
            f"{self._config.messagequeue_url}/api/sessions/{session_id}/history",
            timeout=self._timeout,
        )
        response.raise_for_status()
        data = response.json()
        participants = data.get("participants", [])
        messages = [{"user": entry["user"], "message": entry["message"]} for entry in data.get("messages", [])]
        return participants, messages

    def create_session(
        self, participants: list[dict], session_id: str | None = None
    ) -> str:
        """Create a session (or return existing id if session_id provided and exists)."""
        payload: dict = {"participants": participants}
        if session_id is not None:
            payload["sessionId"] = session_id
        response = httpx.post(
            f"{self._config.messagequeue_url}/api/sessions",
            json=payload,
            timeout=self._timeout,
        )
        response.raise_for_status()
        return response.json()["sessionId"]

    def send_message(self, session_id: str, user: str, message: str) -> None:
        """Append a message to a session."""
        response = httpx.post(
            f"{self._config.messagequeue_url}/api/messages",
            json={"sessionId": session_id, "user": user, "message": message},
            timeout=self._timeout,
        )
        response.raise_for_status()

    def list_agents(self) -> list[dict]:
        """Return all agents from agentmanager (id, name, ...)."""
        response = httpx.get(
            f"{self._config.agentmanager_url}/api/agents",
            timeout=self._timeout,
        )
        response.raise_for_status()
        return response.json()

    def chat(self, agent_id: UUID, messages: list[dict[str, str]]) -> str:
        """Generate the next assistant message for the given agent and message history."""
        response = httpx.post(
            f"{self._config.agentmanager_url}/api/chat",
            json={
                "agent_id": str(agent_id),
                "messages": [{"role": message["role"], "content": message["content"]} for message in messages],
            },
            timeout=120.0,
        )
        response.raise_for_status()
        return response.json()["content"]

    def list_tickets_by_status(self, status: str) -> list[dict]:
        """Return tickets with the given status (e.g. 'todo', 'review')."""
        response = httpx.get(
            f"{self._config.ticketmanager_url}/api/tickets",
            params={"status": status},
            timeout=self._timeout,
        )
        response.raise_for_status()
        return response.json()

    def task_session_id(self, ticket_id: str) -> str:
        """Return the stable session id for a task (RoseHeartbeat-task-{ticket_id})."""
        return f"RoseHeartbeat-task-{ticket_id}"

    def heartbeat_participants(self, assignee: str) -> list[dict]:
        """Return the two participants for a task session: RoseHeartBeat and assignee."""
        return [
            {"name": HEARTBEAT_USER, "isAgent": HEARTBEAT_IS_AGENT},
            {"name": assignee, "isAgent": True},
        ]
