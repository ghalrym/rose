"""FastAPI application entry point and router registration."""

from fastapi import FastAPI

from messagequeue.app.api import messages as messages_router

app = FastAPI(
    title="Message Queue",
    description="Session-based message history with send, poll, and history API.",
)

app.include_router(messages_router.router, prefix="/api", tags=["messages"])
