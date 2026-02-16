"""FastAPI application entry point, router registration, and Discord bot lifespan."""

import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from discordgateway.app.api import config as config_router
from discordgateway.app.api import send_to_channel as send_to_channel_router
from discordgateway.app.config import GatewayConfig
from discordgateway.app.discord.bot import GatewayBot
from discordgateway.app.persistence.channel_assignment_repository import (
    ChannelAssignmentRepository,
)
from discordgateway.app.persistence.config_repository import ConfigRepository
from discordgateway.app.persistence.database import get_connection
from discordgateway.app.services.agentmanager_client import AgentmanagerClient
from discordgateway.app.services.config_service import ConfigService
from discordgateway.app.services.messagequeue_client import MessageQueueClient

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start Discord bot if token is set; store bot in app.state; close on shutdown."""
    connection = get_connection()
    config_repository = ConfigRepository(connection)
    channel_assignment_repository = ChannelAssignmentRepository(connection)
    config_service = ConfigService(
        config_repository, channel_assignment_repository
    )
    gateway_config = GatewayConfig()
    messagequeue_client = MessageQueueClient(gateway_config.messagequeue_url)
    agentmanager_client = AgentmanagerClient(gateway_config.agentmanager_url)
    bot = GatewayBot(
        config_service,
        messagequeue_client,
        agentmanager_client,
        control_panel_url=gateway_config.control_panel_url,
    )
    app.state.discord_bot = bot
    token = config_service.get_token()
    bot_task = None
    if token:
        bot_task = asyncio.create_task(bot.start(token))
        await asyncio.sleep(0.5)
    yield
    if bot_task is not None:
        await bot.close()
        try:
            await asyncio.wait_for(bot_task, timeout=5.0)
        except asyncio.TimeoutError:
            bot_task.cancel()
    connection.close()


app = FastAPI(
    title="DiscordGateway",
    description="Discord bot gateway: relay to message queue, config UI, send-to-channel API.",
    lifespan=lifespan,
)

app.include_router(config_router.router, prefix="/api", tags=["config"])
app.include_router(send_to_channel_router.router, prefix="/api", tags=["send"])

from discordgateway.app.web import routes as web_routes  # noqa: E402

app.include_router(web_routes.router, tags=["web"])

static_path = Path(__file__).resolve().parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
