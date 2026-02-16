"""API routes for config (bot token), channel assignments, and guilds/channels from bot."""

from fastapi import APIRouter, Depends, HTTPException, Request

from discordgateway.app.dependencies import get_config_service
from discordgateway.app.models.config import (
    ChannelAssignmentCreate,
    ChannelAssignmentResponse,
    ConfigResponse,
    ConfigUpdateRequest,
)
from discordgateway.app.services.config_service import ConfigService

from discordgateway.app.api.send_to_channel import STATE_KEY_BOT

router = APIRouter()


@router.get("/config", response_model=ConfigResponse)
def get_config(
    service: ConfigService = Depends(get_config_service),
) -> ConfigResponse:
    """Return current config (token_set, token_preview)."""
    data = service.get_config_response()
    return ConfigResponse(**data)


@router.post("/config", response_model=ConfigResponse)
def update_config(
    payload: ConfigUpdateRequest,
    service: ConfigService = Depends(get_config_service),
) -> ConfigResponse:
    """Set or clear the Discord bot token. Restart or reconnect the bot for changes to take effect."""
    service.set_token(payload.token)
    data = service.get_config_response()
    return ConfigResponse(**data)


@router.get("/channel-assignments", response_model=list[ChannelAssignmentResponse])
def list_channel_assignments(
    service: ConfigService = Depends(get_config_service),
) -> list[ChannelAssignmentResponse]:
    """List all channel-to-agent assignments."""
    assignments = service.list_channel_assignments()
    return [ChannelAssignmentResponse(**assignment) for assignment in assignments]


@router.post("/channel-assignments", response_model=ChannelAssignmentResponse)
def create_channel_assignment(
    payload: ChannelAssignmentCreate,
    service: ConfigService = Depends(get_config_service),
) -> ChannelAssignmentResponse:
    """Create or update a channel assignment (guild + channel -> agent)."""
    service.upsert_channel_assignment(
        payload.guild_id, payload.channel_id, payload.agent_id
    )
    return ChannelAssignmentResponse(
        guild_id=payload.guild_id,
        channel_id=payload.channel_id,
        agent_id=payload.agent_id,
    )


@router.delete("/channel-assignments/{guild_id}/{channel_id}", status_code=204)
def delete_channel_assignment(
    guild_id: str,
    channel_id: str,
    service: ConfigService = Depends(get_config_service),
) -> None:
    """Remove the assignment for this guild and channel."""
    deleted = service.delete_channel_assignment(guild_id, channel_id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="No assignment found for this guild and channel",
        )


@router.get("/guilds")
def list_guilds_and_channels(request: Request) -> list[dict]:
    """Return guilds and their text channels from the Discord bot cache (for UI dropdowns)."""
    bot = getattr(request.app.state, STATE_KEY_BOT, None)
    if bot is None or not bot.is_ready():
        return []
    result = []
    for guild in bot.guilds:
        channels = [
            {"id": str(channel.id), "name": channel.name}
            for channel in guild.text_channels
        ]
        result.append(
            {
                "id": str(guild.id),
                "name": guild.name,
                "channels": sorted(channels, key=lambda channel: channel["name"]),
            }
        )
    return sorted(result, key=lambda guild: guild["name"])
