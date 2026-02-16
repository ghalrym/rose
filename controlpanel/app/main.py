"""FastAPI application entry point and router registration."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from controlpanel.app.api import events as events_router
from controlpanel.app.web import routes as web_routes

app = FastAPI(
    title="Rose Control Panel",
    description="Single-page navigation to Ticket Manager, Agentmanager, Message Queue, Discord Gateway, and Events.",
)

app.include_router(events_router.router)
app.include_router(web_routes.router, tags=["web"])

static_path = Path(__file__).resolve().parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
