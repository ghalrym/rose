"""Main heartbeat loop: chat updates and ticket dispatch."""

import logging
import time
from uuid import UUID

from heartbeat.app.clients import ServiceClient
from heartbeat.app.config import HEARTBEAT_USER, HeartbeatConfig
from heartbeat.app.events_reporter import report_event

logger = logging.getLogger(__name__)


class HeartbeatLoop:
    """Runs the heartbeat loop: process chat updates, dispatch tickets, sleep."""

    def __init__(self, config: HeartbeatConfig, client: ServiceClient | None = None) -> None:
        """Initialize with config and optional client (for tests).

        Args:
            config: Service URLs and sleep interval.
            client: Optional HTTP client; if None, creates one from config.
        """
        self._config = config
        self._client = client or ServiceClient(config)

    def run(self) -> None:
        """Run the loop forever: chat updates, ticket dispatch, then sleep."""
        logger.info("Heartbeat loop starting")
        while True:
            try:
                self._chat_update_step()
                self._ticket_dispatch_step()
            except Exception as error:
                logger.exception("Heartbeat iteration failed: %s", error)
            time.sleep(self._config.sleep_seconds)

    def _chat_update_step(self) -> None:
        """Check sessions with updates, invoke responding agent, post reply to queue."""
        try:
            session_ids = self._client.list_sessions_with_updates()
        except Exception as error:
            logger.warning("Failed to list sessions with updates: %s", error)
            return
        agents_by_name = self._load_agents()
        for session_id in session_ids:
            try:
                self._process_session_update(session_id, agents_by_name)
            except Exception as error:
                logger.warning("Failed to process session %s: %s", session_id, error)

    def _load_agents(self) -> dict[str, str]:
        """Return a map of agent name -> agent id (uuid string)."""
        try:
            agents = self._client.list_agents()
        except Exception as error:
            logger.warning("Failed to list agents: %s", error)
            return {}
        return {agent["name"]: agent["id"] for agent in agents}

    def _process_session_update(self, session_id: str, agents_by_name: dict[str, str]) -> None:
        """Handle one session: get history, choose responding agent, invoke, post reply."""
        if self._config.control_panel_url:
            report_event(
                self._config.control_panel_url,
                "heartbeat",
                "heartbeat.found_message",
                f"Processing new message in session {session_id}",
            )
        participants, messages = self._client.get_session_history(session_id)
        agent_participants = [participant for participant in participants if participant.get("isAgent")]
        if not agent_participants:
            return
        if len(messages) == 0:
            return
        last_sender = messages[-1]["user"]
        if len(agent_participants) == 2:
            # Respond with the agent that did not send the last message
            other_agent = next(
                (participant for participant in agent_participants if participant["name"] != last_sender),
                None,
            )
            if other_agent is None:
                return
            responding_agent_name = other_agent["name"]
        else:
            # One agent: respond as that agent
            responding_agent_name = agent_participants[0]["name"]
        agent_id_str = agents_by_name.get(responding_agent_name)
        if not agent_id_str:
            logger.warning("Agent not found by name: %s", responding_agent_name)
            return
        chat_messages = [
            {
                "role": "assistant" if entry["user"] == responding_agent_name else "user",
                "content": entry["message"],
            }
            for entry in messages
        ]
        try:
            content = self._client.chat(UUID(agent_id_str), chat_messages)
        except Exception as error:
            logger.warning("Chat invoke failed for agent %s: %s", responding_agent_name, error)
            return
        try:
            self._client.send_message(session_id, responding_agent_name, content)
        except Exception as error:
            logger.warning("Failed to send reply to session %s: %s", session_id, error)

    def _ticket_dispatch_step(self) -> None:
        """Fetch todo/review tickets, get-or-create task sessions, send task message if new."""
        try:
            todo_tickets = self._client.list_tickets_by_status("todo")
            review_tickets = self._client.list_tickets_by_status("review")
        except Exception as error:
            logger.warning("Failed to list tickets: %s", error)
            return
        for ticket in todo_tickets + review_tickets:
            try:
                self._dispatch_ticket(ticket)
            except Exception as error:
                logger.warning("Failed to dispatch ticket %s: %s", ticket.get("id"), error)

    def _dispatch_ticket(self, ticket: dict) -> None:
        """Get-or-create task session for ticket; send task message only if history empty."""
        ticket_id = ticket["id"]
        assignee = ticket.get("assignee", "").strip()
        if not assignee:
            return
        session_id = self._client.task_session_id(str(ticket_id))
        participants = self._client.heartbeat_participants(assignee)
        try:
            self._client.create_session(participants, session_id=session_id)
        except Exception as error:
            logger.warning("Failed to create/find session for ticket %s: %s", ticket_id, error)
            return
        try:
            _, messages = self._client.get_session_history(session_id)
        except Exception as error:
            logger.warning("Failed to get history for session %s: %s", session_id, error)
            return
        if messages:
            return
        status = ticket.get("status", "todo")
        title = ticket.get("title", "")
        instructions = ticket.get("instructions", "")
        body = f"Task ({status}): {title}\n\n{instructions}"
        try:
            self._client.send_message(session_id, HEARTBEAT_USER, body)
            if self._config.control_panel_url:
                report_event(
                    self._config.control_panel_url,
                    "heartbeat",
                    "heartbeat.found_task",
                    f"Dispatched task for ticket {ticket_id}: {title!r}",
                )
        except Exception as error:
            logger.warning("Failed to send task message to session %s: %s", session_id, error)
