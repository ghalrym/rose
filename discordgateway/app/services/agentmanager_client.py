"""HTTP client for the agentmanager API."""


class AgentmanagerClient:
    """Facade for agentmanager REST calls (list agents, get agent by id)."""

    def __init__(self, base_url: str, timeout: float = 60.0) -> None:
        """Initialize with agentmanager base URL.

        Args:
            base_url: Base URL for agentmanager (e.g. http://agentmanager:8000).
            timeout: Request timeout in seconds.
        """
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    def list_agents(self) -> list[dict]:
        """Return all agents from agentmanager (id, name, provider, model, ...).

        Returns:
            List of agent dicts with at least "id" (str) and "name" (str).

        Raises:
            httpx.HTTPStatusError: If the request fails.
        """
        import httpx

        response = httpx.get(
            f"{self._base_url}/api/agents",
            timeout=self._timeout,
        )
        response.raise_for_status()
        agents = response.json()
        return [
            {"id": str(agent["id"]), "name": agent["name"], **agent}
            if isinstance(agent.get("id"), str)
            else agent
            for agent in agents
        ]

    def get_agent_name(self, agent_id: str) -> str | None:
        """Return the agent's display name for the given id, or None if not found.

        Args:
            agent_id: Agent UUID string.

        Returns:
            Agent name or None.
        """
        import httpx

        try:
            response = httpx.get(
                f"{self._base_url}/api/agents/{agent_id}",
                timeout=self._timeout,
            )
            response.raise_for_status()
            return response.json().get("name")
        except httpx.HTTPStatusError:
            return None
