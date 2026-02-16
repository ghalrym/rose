"""Pydantic models for bot config and API."""

from pydantic import BaseModel, Field


class ConfigResponse(BaseModel):
    """Current config (token masked for display)."""

    token_set: bool = Field(..., description="Whether a Discord bot token is configured")
    token_preview: str | None = Field(
        default=None,
        description="Last few characters of token for confirmation, or None if not set",
    )


class ConfigUpdateRequest(BaseModel):
    """Request body for setting the Discord bot token."""

    token: str | None = Field(default=None, description="Bot token; omit or empty to clear")


class ChannelAssignmentCreate(BaseModel):
    """Request body for creating a channel assignment."""

    guild_id: str = Field(..., description="Discord guild (server) id")
    channel_id: str = Field(..., description="Discord channel id")
    agent_id: str = Field(..., description="Agent UUID from agentmanager")


class ChannelAssignmentResponse(BaseModel):
    """One channel assignment (guild, channel, agent id)."""

    guild_id: str = Field(..., description="Discord guild id")
    channel_id: str = Field(..., description="Discord channel id")
    agent_id: str = Field(..., description="Agent UUID")


class SendToChannelRequest(BaseModel):
    """Request body for sending a message to a Discord channel."""

    channel_id: str = Field(..., description="Discord channel snowflake id")
    message: str = Field(..., description="Message text to send")


class SendToChannelResponse(BaseModel):
    """Response after sending to channel."""

    ok: bool = Field(True, description="Whether the message was sent")
