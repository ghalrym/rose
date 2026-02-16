"""Web UI routes: config (token), channel assignments, guilds/channels from bot."""

from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from discordgateway.app.api.send_to_channel import STATE_KEY_BOT
from discordgateway.app.dependencies import (
    get_agentmanager_client,
    get_config_service,
)
from discordgateway.app.services.agentmanager_client import AgentmanagerClient
from discordgateway.app.services.config_service import ConfigService

router = APIRouter()
templates_path = Path(__file__).resolve().parent / "templates"
templates = Jinja2Templates(directory=str(templates_path))


@router.get("/", response_class=HTMLResponse)
def index(
    request: Request,
    config_service: ConfigService = Depends(get_config_service),
    agentmanager_client: AgentmanagerClient = Depends(get_agentmanager_client),
) -> HTMLResponse:
    """Render config and channel assignments UI."""
    config = config_service.get_config_response()
    assignments = config_service.list_channel_assignments()
    agents = []
    try:
        agents = agentmanager_client.list_agents()
    except Exception:
        pass
    guilds = []
    bot = getattr(request.app.state, STATE_KEY_BOT, None)
    if bot is not None and bot.is_ready():
        for guild in bot.guilds:
            channels = [
                {"id": str(channel.id), "name": channel.name}
                for channel in guild.text_channels
            ]
            guilds.append(
                {
                    "id": str(guild.id),
                    "name": guild.name,
                    "channels": sorted(channels, key=lambda channel: channel["name"]),
                }
            )
        guilds.sort(key=lambda guild: guild["name"])
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "config": config,
            "assignments": assignments,
            "agents": agents,
            "guilds": guilds,
        },
    )


@router.post("/config")
async def update_config_from_form(
    request: Request,
    config_service: ConfigService = Depends(get_config_service),
) -> RedirectResponse:
    """Handle form submit to set or clear the Discord bot token."""
    form = await request.form()
    token = form.get("token", "").strip() or None
    config_service.set_token(token)
    return RedirectResponse(url="/", status_code=303)


@router.post("/channel-assignments")
async def create_assignment_from_form(
    request: Request,
    config_service: ConfigService = Depends(get_config_service),
) -> RedirectResponse:
    """Handle form submit to add or update a channel assignment."""
    form = await request.form()
    guild_id = form.get("guild_id", "").strip()
    channel_id = form.get("channel_id", "").strip()
    agent_id = form.get("agent_id", "").strip()
    if guild_id and channel_id and agent_id:
        config_service.upsert_channel_assignment(guild_id, channel_id, agent_id)
    return RedirectResponse(url="/", status_code=303)


@router.get("/channel-assignments/{guild_id}/{channel_id}/delete")
def delete_assignment(
    guild_id: str,
    channel_id: str,
    config_service: ConfigService = Depends(get_config_service),
) -> RedirectResponse:
    """Remove a channel assignment and redirect to index."""
    config_service.delete_channel_assignment(guild_id, channel_id)
    return RedirectResponse(url="/", status_code=303)
