"""Agent REST API routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from agentmanager.app.dependencies import get_agent_service
from agentmanager.app.models.agent import Agent, AgentCreate, AgentUpdate
from agentmanager.app.services.agent_service import AgentService
from agentmanager.app.services.events_reporter import report_event

router = APIRouter()


@router.post("/agents", response_model=Agent)
def create_agent(
    payload: AgentCreate,
    service: AgentService = Depends(get_agent_service),
) -> Agent:
    """Create a new agent. Id and timestamps are set server-side."""
    agent = service.create(payload)
    report_event("agentmanager", "agent.created", f"Agent {agent.name} created")
    return agent


@router.get("/agents", response_model=list[Agent])
def list_agents(
    service: AgentService = Depends(get_agent_service),
) -> list[Agent]:
    """List all agents."""
    return service.list_all()


@router.get("/agents/{agent_id}", response_model=Agent)
def get_agent(
    agent_id: UUID,
    service: AgentService = Depends(get_agent_service),
) -> Agent:
    """Return a single agent by id."""
    agent = service.get_by_id(agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.put("/agents/{agent_id}", response_model=Agent)
def update_agent(
    agent_id: UUID,
    payload: AgentUpdate,
    service: AgentService = Depends(get_agent_service),
) -> Agent:
    """Update an agent. Only provided fields are updated."""
    agent = service.update(agent_id, payload)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.delete("/agents/{agent_id}", status_code=204)
def delete_agent(
    agent_id: UUID,
    service: AgentService = Depends(get_agent_service),
) -> None:
    """Delete an agent by id."""
    deleted = service.delete(agent_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Agent not found")
