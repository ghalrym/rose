"""API route for sending a message to a Discord channel (out-of-band)."""

from fastapi import APIRouter, HTTPException, Request

from discordgateway.app.models.config import SendToChannelRequest, SendToChannelResponse

router = APIRouter()

STATE_KEY_BOT = "discord_bot"


@router.post("/send-to-channel", response_model=SendToChannelResponse)
async def send_to_channel(
    payload: SendToChannelRequest,
    request: Request,
) -> SendToChannelResponse:
    """Send a message to a Discord channel from the bot. Used for out-of-band notifications (e.g. task done later)."""
    bot = getattr(request.app.state, STATE_KEY_BOT, None)
    if bot is None or not bot.is_ready():
        raise HTTPException(
            status_code=404,
            detail="Discord bot not connected or channel not found",
        )
    channel = bot.get_channel(int(payload.channel_id))
    if channel is None:
        raise HTTPException(
            status_code=404,
            detail="Channel not found or bot not in guild",
        )
    await channel.send(payload.message)
    return SendToChannelResponse(ok=True)
