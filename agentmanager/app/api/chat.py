"""Chat API routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from agentmanager.app.dependencies import get_chat_service
from agentmanager.app.services.chat_service import ChatService
from agentmanager.app.services.events_reporter import report_event

router = APIRouter()


class ChatMessage(BaseModel):
    """A single message in the conversation."""

    role: str = Field(..., description="'user', 'assistant', or 'system'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Request body for chat endpoint."""

    agent_id: UUID = Field(..., description="Agent to use for the response")
    messages: list[ChatMessage] = Field(
        ...,
        description="Full conversation history; last message is the current user message",
    )


class ChatResponse(BaseModel):
    """Response with the generated assistant message."""

    content: str = Field(..., description="The assistant's reply")


@router.post("/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    """Generate the next assistant message. Caller sends full history; we return the reply."""
    try:
        messages = [
            {"role": message.role, "content": message.content}
            for message in payload.messages
        ]
        content = await service.generate_response(payload.agent_id, messages)
        report_event(
            "agentmanager",
            "agent.requested",
            f"Chat request for agent {payload.agent_id}",
        )
        return ChatResponse(content=content)
    except ValueError as error:
        if "not found" in str(error).lower():
            raise HTTPException(status_code=404, detail=str(error)) from error
        raise HTTPException(status_code=400, detail=str(error)) from error
    except RuntimeError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
