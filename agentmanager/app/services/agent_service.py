"""Application service for agent CRUD operations."""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from agentmanager.app.models.agent import (
    Agent,
    AgentCreate,
    AgentUpdate,
)
from agentmanager.app.persistence.agent_repository import AgentRepository


class AgentService:
    """Orchestrates agent creation, updates, and queries."""

    def __init__(self, repository: AgentRepository) -> None:
        """Initialize with an agent repository.

        Args:
            repository: The repository used for persistence.
        """
        self._repository = repository

    def create(self, payload: AgentCreate) -> Agent:
        """Create a new agent with a generated id and timestamps.

        Args:
            payload: Creation payload (name, provider, model, agent_md, mcp_servers).

        Returns:
            The created Agent.

        Raises:
            sqlite3.IntegrityError: If a duplicate id is generated (extremely unlikely).
        """
        now = datetime.now(timezone.utc)
        agent = Agent(
            id=uuid4(),
            name=payload.name,
            provider=payload.provider,
            model=payload.model,
            agent_md=payload.agent_md,
            mcp_servers=payload.mcp_servers,
            ollama_base_url=payload.ollama_base_url,
            created_at=now,
            updated_at=now,
        )
        return self._repository.create(agent)

    def get_by_id(self, agent_id: UUID) -> Agent | None:
        """Return an agent by id, or None if not found."""
        return self._repository.get_by_id(agent_id)

    def list_all(self) -> list[Agent]:
        """List all agents."""
        return self._repository.list_all()

    def update(self, agent_id: UUID, payload: AgentUpdate) -> Agent | None:
        """Update an agent by id. Returns None if the agent does not exist."""
        return self._repository.update(agent_id, payload)

    def delete(self, agent_id: UUID) -> bool:
        """Delete an agent by id. Returns True if deleted, False if not found."""
        return self._repository.delete(agent_id)
