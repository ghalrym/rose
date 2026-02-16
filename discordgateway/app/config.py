"""Gateway configuration from environment."""

import os


class GatewayConfig:
    """Configuration for DiscordGateway (service URLs from env)."""

    def __init__(
        self,
        messagequeue_url: str | None = None,
        agentmanager_url: str | None = None,
        control_panel_url: str | None = None,
    ) -> None:
        """Initialize from env or provided values.

        Args:
            messagequeue_url: Base URL for message queue. Defaults to env MESSAGEQUEUE_URL or http://messagequeue:8000.
            agentmanager_url: Base URL for agentmanager. Defaults to env AGENTMANAGER_URL or http://agentmanager:8000.
            control_panel_url: Base URL for control panel (events). Defaults to env CONTROL_PANEL_URL; empty = no reporting.
        """
        self.messagequeue_url = (
            messagequeue_url
            or os.environ.get("MESSAGEQUEUE_URL", "http://messagequeue:8000")
        ).rstrip("/")
        self.agentmanager_url = (
            agentmanager_url
            or os.environ.get("AGENTMANAGER_URL", "http://agentmanager:8000")
        ).rstrip("/")
        raw = control_panel_url or os.environ.get("CONTROL_PANEL_URL", "")
        self.control_panel_url = raw.strip() or None
