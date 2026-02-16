"""Message queue API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query, Response

from messagequeue.app.dependencies import get_queue_service
from messagequeue.app.models.message import (
    CreateSessionRequest,
    CreateSessionResponse,
    HistoryResponse,
    PollResponse,
    SendMessageRequest,
    SendMessageResponse,
    SessionsWithUpdatesResponse,
)
from messagequeue.app.services.queue_service import QueueService, SessionNotFoundError

router = APIRouter()


@router.post("/sessions", response_model=CreateSessionResponse)
def create_session(
    payload: CreateSessionRequest,
    response: Response,
    service: QueueService = Depends(get_queue_service),
) -> CreateSessionResponse:
    """Create a session with exactly two participants (name, isAgent). Returns session id.
    If sessionId is provided and that session exists, returns it (idempotent, 200)."""
    session_id, created = service.create_session(
        payload.participants, session_id=payload.sessionId
    )
    response.status_code = 201 if created else 200
    return CreateSessionResponse(sessionId=session_id)


@router.post("/sessions/find", response_model=CreateSessionResponse)
def find_session(
    payload: CreateSessionRequest,
    service: QueueService = Depends(get_queue_service),
) -> CreateSessionResponse:
    """Find a session between the two given participants (name, isAgent). Order-independent. 404 if not found."""
    session_id = service.find_session_by_participants(payload.participants)
    if session_id is None:
        raise HTTPException(
            status_code=404,
            detail="No session found for these two participants",
        )
    return CreateSessionResponse(sessionId=session_id)


@router.post("/messages", response_model=SendMessageResponse, status_code=201)
def send_message(
    payload: SendMessageRequest,
    service: QueueService = Depends(get_queue_service),
) -> SendMessageResponse:
    """Send a message in a session. Session must exist (create via POST /api/sessions)."""
    try:
        service.send_message(
            session_id=payload.sessionId,
            user=payload.user,
            message=payload.message,
        )
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return SendMessageResponse(ok=True)


@router.get("/poll", response_model=PollResponse)
def poll(
    sessionId: str | None = Query(None, description="Session to check for unseen messages"),
    service: QueueService = Depends(get_queue_service),
) -> PollResponse:
    """Return whether there is a new unseen message in the session. No side effects."""
    if sessionId is None or sessionId.strip() == "":
        return PollResponse(has_unseen=False)
    return PollResponse(has_unseen=service.has_unseen(sessionId.strip()))


@router.get("/sessions/updated", response_model=SessionsWithUpdatesResponse)
def list_sessions_with_updates(
    service: QueueService = Depends(get_queue_service),
) -> SessionsWithUpdatesResponse:
    """Return all session ids that have an unseen update."""
    session_ids = service.list_sessions_with_updates()
    return SessionsWithUpdatesResponse(session_ids=session_ids)


@router.get("/sessions/{session_id}/history", response_model=HistoryResponse)
def get_history(
    session_id: str,
    clear_unseen: bool = Query(True, description="Clear the unseen flag after reading"),
    service: QueueService = Depends(get_queue_service),
) -> HistoryResponse:
    """Return full conversation history (participants + messages).
    When clear_unseen is True (default), also clear the unseen flag."""
    try:
        participants, entries = service.get_history(session_id, clear_unseen=clear_unseen)
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return HistoryResponse(participants=participants, messages=entries)
