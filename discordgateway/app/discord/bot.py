"""Discord bot: relay messages to queue and wait for agent reply by checking history."""

import asyncio
import logging

import discord

from discordgateway.app.services.agentmanager_client import AgentmanagerClient
from discordgateway.app.services.config_service import ConfigService
from discordgateway.app.services.events_reporter import report_event
from discordgateway.app.services.messagequeue_client import MessageQueueClient

logger = logging.getLogger(__name__)

HISTORY_POLL_INTERVAL_SECONDS = 2.0
HISTORY_POLL_TIMEOUT_SECONDS = 300.0


def _session_id(guild_id: int, channel_id: int, user_id: int) -> str:
    """Stable session id for a Discord user in a channel."""
    return f"discord-{guild_id}-{channel_id}-{user_id}"


class GatewayBot(discord.Client):
    """Discord client that relays channel messages to the message queue and sends agent replies back."""

    def __init__(
        self,
        config_service: ConfigService,
        messagequeue_client: MessageQueueClient,
        agentmanager_client: AgentmanagerClient,
        *,
        control_panel_url: str | None = None,
        intents: discord.Intents | None = None,
    ) -> None:
        """Initialize with config and HTTP clients.

        Args:
            config_service: For token and channel-to-agent assignments.
            messagequeue_client: For create_session, send_message, get_history.
            agentmanager_client: For resolving agent id to name.
            control_panel_url: Optional base URL for reporting events.
            intents: Discord intents; defaults to default + message content.
        """
        if intents is None:
            intents = discord.Intents.default()
            intents.message_content = True
            intents.guilds = True
        super().__init__(intents=intents)
        self._config_service = config_service
        self._messagequeue_client = messagequeue_client
        self._agentmanager_client = agentmanager_client
        self._control_panel_url = control_panel_url

    async def on_ready(self) -> None:
        """Log when the bot is connected."""
        logger.info("Discord bot ready: %s", self.user)

    async def on_message(self, message: discord.Message) -> None:
        """On Discord message: resolve agent, relay to queue, loop until agent reply, send reply to channel."""
        if message.author == self.user or message.author.bot:
            return
        if message.guild is None:
            return
        guild_id = message.guild.id
        channel_id = message.channel.id
        user_id = message.author.id
        agent_id = self._config_service.get_agent_id_for_channel(
            str(guild_id), str(channel_id)
        )
        if not agent_id:
            return
        agent_name = self._agentmanager_client.get_agent_name(agent_id)
        if not agent_name:
            logger.warning("Agent not found for id %s", agent_id)
            return
        user_name = message.author.display_name or str(user_id)
        session_id = _session_id(guild_id, channel_id, user_id)
        participants = [
            {"name": user_name, "isAgent": False},
            {"name": agent_name, "isAgent": True},
        ]
        try:
            self._messagequeue_client.create_session(
                participants, session_id=session_id
            )
            self._messagequeue_client.send_message(
                session_id, user_name, message.content
            )
        except Exception as error:
            logger.exception("Failed to create session or send message: %s", error)
            await message.channel.send(
                "Sorry, I couldn't relay that to the agent. Please try again later."
            )
            return
        if self._control_panel_url:
            loop = asyncio.get_event_loop()
            loop.run_in_executor(
                None,
                lambda: report_event(
                    self._control_panel_url,
                    "discordgateway",
                    "discord.user_message",
                    f"User {user_name} in channel: {message.content[:100]!r}",
                ),
            )
        reply_text = await self._wait_for_agent_reply(
            session_id, agent_name, channel=message.channel
        )
        if reply_text is not None:
            await message.channel.send(reply_text)
            if self._control_panel_url:
                loop = asyncio.get_event_loop()
                loop.run_in_executor(
                    None,
                    lambda: report_event(
                        self._control_panel_url,
                        "discordgateway",
                        "discord.agent_reply",
                        f"Agent {agent_name} replied in channel",
                    ),
                )

    async def _wait_for_agent_reply(
        self,
        session_id: str,
        agent_name: str,
        *,
        channel: discord.abc.Messageable,
    ) -> str | None:
        """Loop get_history(clear_unseen=False) until last message is from the agent; then clear and return that message."""
        loop = asyncio.get_event_loop()
        elapsed = 0.0
        while elapsed < HISTORY_POLL_TIMEOUT_SECONDS:
            participants, messages = await loop.run_in_executor(
                None,
                lambda: self._messagequeue_client.get_history(
                    session_id, clear_unseen=False
                ),
            )
            if messages:
                last = messages[-1]
                if last["user"] == agent_name:
                    reply_text = last["message"]
                    await loop.run_in_executor(
                        None,
                        lambda: self._messagequeue_client.get_history(
                            session_id, clear_unseen=True
                        ),
                    )
                    return reply_text
            await asyncio.sleep(HISTORY_POLL_INTERVAL_SECONDS)
            elapsed += HISTORY_POLL_INTERVAL_SECONDS
        await channel.send(
            "The agent did not respond in time. Please try again or check the service."
        )
        return None
