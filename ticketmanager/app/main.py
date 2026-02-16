"""FastAPI application entry point and router registration."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from ticketmanager.app.api import tickets as tickets_router
from ticketmanager.app.web import routes as web_routes

app = FastAPI(title="Ticket Manager", description="Kanban ticketing API and UI")

app.include_router(tickets_router.router, prefix="/api", tags=["tickets"])
app.include_router(web_routes.router, tags=["web"])

static_path = Path(__file__).resolve().parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
