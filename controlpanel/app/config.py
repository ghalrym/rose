"""Service URL configuration for the control panel.

URLs are the base URLs that the browser will use to load each service
(e.g. http://localhost:8000). In Docker, the browser runs on the host,
so these typically remain localhost with the published ports.
"""

import os


def _get_url(env_key: str, default: str) -> str:
    value = os.environ.get(env_key, default).strip()
    return value.rstrip("/") if value else default


class ServiceUrls:
    """Base URLs for each platform service, used for iframe and links."""

    def __init__(self) -> None:
        self.ticketmanager = _get_url(
            "TICKETMANAGER_URL",
            "http://localhost:8000",
        )
        self.agentmanager = _get_url(
            "AGENTMANAGER_URL",
            "http://localhost:8001",
        )
        self.messagequeue = _get_url(
            "MESSAGEQUEUE_URL",
            "http://localhost:8002",
        )
        self.discordgateway = _get_url(
            "DISCORDGATEWAY_URL",
            "http://localhost:8003",
        )

    def as_context(self) -> dict[str, str]:
        """Return a dict suitable for Jinja template context."""
        return {
            "ticketmanager_url": self.ticketmanager,
            "agentmanager_url": self.agentmanager,
            "messagequeue_url": self.messagequeue,
            "discordgateway_url": self.discordgateway,
        }
