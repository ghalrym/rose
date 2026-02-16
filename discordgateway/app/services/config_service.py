"""Service for gateway config and channel assignments."""

from discordgateway.app.persistence.channel_assignment_repository import (
    ChannelAssignmentRepository,
)
from discordgateway.app.persistence.config_repository import ConfigRepository


class ConfigService:
    """Orchestrates config and channel assignment operations."""

    def __init__(
        self,
        config_repository: ConfigRepository,
        channel_assignment_repository: ChannelAssignmentRepository,
    ) -> None:
        """Initialize with config and channel assignment repositories.

        Args:
            config_repository: Repository for bot token and other config.
            channel_assignment_repository: Repository for channel-to-agent assignments.
        """
        self._config_repository = config_repository
        self._channel_assignment_repository = channel_assignment_repository

    def get_config_response(self) -> dict:
        """Return current config for API (token_set, token_preview)."""
        token = self._config_repository.get_token()
        preview = self._config_repository.get_token_preview()
        return {
            "token_set": bool(token),
            "token_preview": preview,
        }

    def set_token(self, token: str | None) -> None:
        """Set or clear the Discord bot token."""
        self._config_repository.set_token(token)

    def get_token(self) -> str | None:
        """Return the raw token (for the bot); None if not set."""
        return self._config_repository.get_token()

    def list_channel_assignments(self) -> list[dict]:
        """Return all channel assignments as list of {guild_id, channel_id, agent_id}."""
        rows = self._channel_assignment_repository.list_all()
        return [
            {"guild_id": guild_id, "channel_id": channel_id, "agent_id": agent_id}
            for guild_id, channel_id, agent_id in rows
        ]

    def get_agent_id_for_channel(self, guild_id: str, channel_id: str) -> str | None:
        """Return the agent_id assigned to this guild+channel, or None."""
        return self._channel_assignment_repository.get_agent_id(guild_id, channel_id)

    def upsert_channel_assignment(
        self, guild_id: str, channel_id: str, agent_id: str
    ) -> None:
        """Create or update the assignment for this guild and channel."""
        self._channel_assignment_repository.upsert(guild_id, channel_id, agent_id)

    def delete_channel_assignment(self, guild_id: str, channel_id: str) -> bool:
        """Remove the assignment. Return True if an assignment was deleted."""
        return self._channel_assignment_repository.delete(guild_id, channel_id)
