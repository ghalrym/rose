"""Configuration loaded from environment."""

import os


HEARTBEAT_USER = "RoseHeartBeat"
HEARTBEAT_IS_AGENT = False

DEFAULT_AGENTMANAGER_URL = "http://agentmanager:8000"
DEFAULT_MESSAGEQUEUE_URL = "http://messagequeue:8000"
DEFAULT_TICKETMANAGER_URL = "http://web:8000"
DEFAULT_SLEEP_SECONDS = 10


class HeartbeatConfig:
    """Configuration for the heartbeat service.

    Base URLs for agentmanager, messagequeue, and ticketmanager are read from
    environment variables with fallbacks for Docker Compose service names.
    """

    def __init__(
        self,
        agentmanager_url: str | None = None,
        messagequeue_url: str | None = None,
        ticketmanager_url: str | None = None,
        control_panel_url: str | None = None,
        sleep_seconds: float | None = None,
    ) -> None:
        """Initialize from arguments or environment.

        Args:
            agentmanager_url: Base URL for agentmanager API.
            messagequeue_url: Base URL for message queue API.
            ticketmanager_url: Base URL for ticketmanager API (web service).
            control_panel_url: Base URL for control panel (events). Empty = no reporting.
            sleep_seconds: Seconds to sleep between loop iterations.
        """
        self.agentmanager_url = (
            agentmanager_url
            or os.environ.get("AGENTMANAGER_URL", DEFAULT_AGENTMANAGER_URL)
        ).rstrip("/")
        self.messagequeue_url = (
            messagequeue_url
            or os.environ.get("MESSAGEQUEUE_URL", DEFAULT_MESSAGEQUEUE_URL)
        ).rstrip("/")
        self.ticketmanager_url = (
            ticketmanager_url
            or os.environ.get("TICKETMANAGER_URL", DEFAULT_TICKETMANAGER_URL)
        ).rstrip("/")
        raw = control_panel_url or os.environ.get("CONTROL_PANEL_URL", "")
        self.control_panel_url = raw.strip() or None
        self.sleep_seconds = sleep_seconds or float(
            os.environ.get("HEARTBEAT_SLEEP_SECONDS", str(DEFAULT_SLEEP_SECONDS))
        )
