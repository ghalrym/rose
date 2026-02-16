"""Message and session API models."""

from pydantic import BaseModel, Field


class Participant(BaseModel):
    """One participant in a session (name and whether they are an agent)."""

    name: str = Field(..., description="Display name of the participant")
    isAgent: bool = Field(..., description="Whether this participant is an agent")


class CreateSessionRequest(BaseModel):
    """Request body for creating a session. Exactly two participants required."""

    participants: list[Participant] = Field(
        ...,
        min_length=2,
        max_length=2,
        description="The two participants in the session (name, isAgent)",
    )
    sessionId: str | None = Field(
        default=None,
        description="Optional session id; if provided and session exists, returns it (idempotent)",
    )


class CreateSessionResponse(BaseModel):
    """Response after creating a session."""

    sessionId: str = Field(..., description="The created session id")


class SendMessageRequest(BaseModel):
    """Request body for sending a message."""

    sessionId: str = Field(..., description="Session (conversation) identifier")
    user: str = Field(..., description="Sender identifier")
    message: str = Field(..., description="Message content")


class SendMessageResponse(BaseModel):
    """Response after sending a message."""

    ok: bool = Field(True, description="Whether the message was accepted")


class PollResponse(BaseModel):
    """Response for poll endpoint."""

    has_unseen: bool = Field(..., description="Whether there is a new unseen message in the session")


class HistoryEntry(BaseModel):
    """A single entry in conversation history."""

    user: str = Field(..., description="Sender identifier")
    message: str = Field(..., description="Message content")


class HistoryResponse(BaseModel):
    """Full conversation history for a session, including participants."""

    participants: list[Participant] = Field(
        default_factory=list,
        description="The two participants (name, isAgent) defined when the session was created",
    )
    messages: list[HistoryEntry] = Field(
        default_factory=list,
        description="Ordered list of conversation entries",
    )


class SessionsWithUpdatesResponse(BaseModel):
    """List of session ids that have an unseen update."""

    session_ids: list[str] = Field(
        default_factory=list,
        description="Session ids with has_unseen set",
    )
