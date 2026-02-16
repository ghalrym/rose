"""FastAPI application entry point and router registration."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from agentmanager.app.api import agents as agents_router
from agentmanager.app.api import chat as chat_router
from agentmanager.app.web import routes as web_routes

app = FastAPI(
    title="Agentmanager",
    description="LLM agent management with Ollama/OpenAI, MCP tools, and AGENT.md",
)

app.include_router(agents_router.router, prefix="/api", tags=["agents"])
app.include_router(chat_router.router, prefix="/api", tags=["chat"])
app.include_router(web_routes.router, tags=["web"])

static_path = Path(__file__).resolve().parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
