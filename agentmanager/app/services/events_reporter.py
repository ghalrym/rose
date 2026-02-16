"""Report platform events to the control panel. Fire-and-forget; failures are logged only."""

import logging
import os

import httpx

logger = logging.getLogger(__name__)


def report_event(
    source: str,
    event: str,
    message: str | None = None,
) -> None:
    """POST an event to the control panel if CONTROL_PANEL_URL is set. Does not raise."""
    base_url = os.environ.get("CONTROL_PANEL_URL", "").strip()
    if not base_url:
        return
    url = f"{base_url.rstrip('/')}/api/events"
    payload = {"source": source, "event": event}
    if message is not None:
        payload["message"] = message
    try:
        httpx.post(url, json=payload, timeout=2.0)
    except Exception as error:
        logger.debug("Failed to report event to control panel: %s", error)
