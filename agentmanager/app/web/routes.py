"""Web UI routes: agent list, create, and edit."""

import json
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from agentmanager.app.dependencies import get_agent_service
from agentmanager.app.models.agent import AgentCreate, AgentUpdate, LlmProvider, McpServerConfig
from agentmanager.app.services.agent_service import AgentService
from agentmanager.app.services.events_reporter import report_event

router = APIRouter()
templates_path = Path(__file__).resolve().parent / "templates"
templates = Jinja2Templates(directory=str(templates_path))


@router.get("/", response_class=HTMLResponse)
def agents_list_page(
    request: Request,
    service: AgentService = Depends(get_agent_service),
) -> HTMLResponse:
    """Render the list of agents with link to create."""
    agents = service.list_all()
    return templates.TemplateResponse(
        request=request,
        name="agents_list.html",
        context={"agents": agents},
    )


@router.get("/agents/new", response_class=HTMLResponse)
def new_agent_page(request: Request) -> HTMLResponse:
    """Render the create-agent form."""
    return templates.TemplateResponse(
        request=request,
        name="agent_form.html",
        context={
            "agent": None,
            "providers": [p.value for p in LlmProvider],
            "mcp_servers_json": "",
        },
    )


@router.post("/agents")
async def create_agent_from_form(
    request: Request,
    service: AgentService = Depends(get_agent_service),
) -> RedirectResponse:
    """Handle form submit to create an agent; redirects to list."""
    form = await request.form()
    name = form.get("name", "").strip() or "Unnamed agent"
    provider_value = form.get("provider", "").strip() or LlmProvider.OLLAMA.value
    try:
        provider = LlmProvider(provider_value)
    except ValueError:
        provider = LlmProvider.OLLAMA
    model = form.get("model", "").strip() or "llama3"
    agent_md = form.get("agent_md", "").strip()
    ollama_base_url = form.get("ollama_base_url", "").strip() or None
    mcp_servers: list[McpServerConfig] = []
    mcp_raw = form.get("mcp_servers", "").strip()
    if mcp_raw:
        try:
            parsed = json.loads(mcp_raw)
            if isinstance(parsed, list):
                for item in parsed:
                    if isinstance(item, dict):
                        mcp_servers.append(
                            McpServerConfig(
                                name=item.get("name", "default"),
                                transport=item.get("transport", "stdio"),
                                command=item.get("command"),
                                args=item.get("args"),
                                url=item.get("url"),
                                headers=item.get("headers"),
                            )
                        )
            elif isinstance(parsed, dict):
                for key, value in parsed.items():
                    if isinstance(value, dict):
                        mcp_servers.append(
                            McpServerConfig(
                                name=key,
                                transport=value.get("transport", "stdio"),
                                command=value.get("command"),
                                args=value.get("args"),
                                url=value.get("url"),
                                headers=value.get("headers"),
                            )
                        )
        except json.JSONDecodeError:
            pass
    payload = AgentCreate(
        name=name,
        provider=provider,
        model=model,
        agent_md=agent_md,
        mcp_servers=mcp_servers,
        ollama_base_url=ollama_base_url,
    )
    agent = service.create(payload)
    report_event("agentmanager", "agent.created", f"Agent {agent.name} created")
    return RedirectResponse(url="/", status_code=303)


@router.get(
    "/agents/{agent_id}/edit",
    response_class=HTMLResponse,
    response_model=None,
)
def edit_agent_page(
    request: Request,
    agent_id: UUID,
    service: AgentService = Depends(get_agent_service),
) -> HTMLResponse | RedirectResponse:
    """Render the edit-agent form."""
    agent = service.get_by_id(agent_id)
    if agent is None:
        return RedirectResponse(url="/", status_code=303)
    mcp_servers_json = (
        json.dumps([server.model_dump() for server in agent.mcp_servers], indent=2)
        if agent.mcp_servers
        else ""
    )
    return templates.TemplateResponse(
        request=request,
        name="agent_form.html",
        context={
            "agent": agent,
            "providers": [p.value for p in LlmProvider],
            "edit": True,
            "mcp_servers_json": mcp_servers_json,
        },
    )


@router.post("/agents/{agent_id}")
async def update_agent_from_form(
    agent_id: UUID,
    request: Request,
    service: AgentService = Depends(get_agent_service),
) -> RedirectResponse:
    """Handle form submit to update an agent; redirects to list."""
    agent = service.get_by_id(agent_id)
    if agent is None:
        return RedirectResponse(url="/", status_code=303)
    form = await request.form()
    name = form.get("name", "").strip() or agent.name
    provider_value = form.get("provider", "").strip() or agent.provider.value
    try:
        provider = LlmProvider(provider_value)
    except ValueError:
        provider = agent.provider
    model = form.get("model", "").strip() or agent.model
    agent_md_raw = form.get("agent_md")
    agent_md = (
        agent_md_raw.strip() if agent_md_raw is not None else agent.agent_md
    )
    ollama_base_url_raw = form.get("ollama_base_url")
    ollama_base_url = (
        ollama_base_url_raw.strip() or None
        if ollama_base_url_raw is not None
        else agent.ollama_base_url
    )
    mcp_servers: list[McpServerConfig] | None = None
    mcp_raw = form.get("mcp_servers", "").strip()
    if mcp_raw:
        mcp_servers = []
        try:
            parsed = json.loads(mcp_raw)
            if isinstance(parsed, list):
                for item in parsed:
                    if isinstance(item, dict):
                        mcp_servers.append(
                            McpServerConfig(
                                name=item.get("name", "default"),
                                transport=item.get("transport", "stdio"),
                                command=item.get("command"),
                                args=item.get("args"),
                                url=item.get("url"),
                                headers=item.get("headers"),
                            )
                        )
            elif isinstance(parsed, dict):
                for key, value in parsed.items():
                    if isinstance(value, dict):
                        mcp_servers.append(
                            McpServerConfig(
                                name=key,
                                transport=value.get("transport", "stdio"),
                                command=value.get("command"),
                                args=value.get("args"),
                                url=value.get("url"),
                                headers=value.get("headers"),
                            )
                        )
        except json.JSONDecodeError:
            pass
    payload = AgentUpdate(
        name=name,
        provider=provider,
        model=model,
        agent_md=agent_md,
        ollama_base_url=ollama_base_url,
        mcp_servers=mcp_servers,
    )
    service.update(agent_id, payload)
    return RedirectResponse(url="/", status_code=303)


@router.post("/agents/{agent_id}/delete")
def delete_agent_from_form(
    agent_id: UUID,
    service: AgentService = Depends(get_agent_service),
) -> RedirectResponse:
    """Handle form submit to delete an agent; redirects to list."""
    service.delete(agent_id)
    return RedirectResponse(url="/", status_code=303)
