"""Agent domain and API models."""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class LlmProvider(str, Enum):
    """Supported LLM backend."""

    OLLAMA = "ollama"
    OPENAI = "openai"


class McpServerConfig(BaseModel):
    """Configuration for one MCP server connection."""

    name: str = Field(..., description="Server identifier for tool prefixing")
    transport: str = Field(..., description="'stdio' or 'http'")
    command: str | None = Field(None, description="Command for stdio transport")
    args: list[str] | None = Field(None, description="Arguments for stdio transport")
    url: str | None = Field(None, description="URL for http transport")
    headers: dict[str, str] | None = Field(None, description="Optional headers for http")

    model_config = {"from_attributes": True}


class Agent(BaseModel):
    """A single agent with LLM and optional MCP config."""

    id: UUID
    name: str
    provider: LlmProvider
    model: str
    agent_md: str
    mcp_servers: list[McpServerConfig]
    ollama_base_url: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_row(cls, row: object) -> "Agent":
        """Build an Agent from a database row (e.g. sqlite3.Row).

        Args:
            row: Row with keys id, name, provider, model, agent_md, mcp_config,
                 ollama_base_url (optional), created_at, updated_at.

        Returns:
            An Agent instance.

        Raises:
            KeyError: If a required key is missing from the row.
            ValueError: If id or datetimes cannot be parsed.
        """
        import json

        data = dict(row)
        mcp_config_raw = data.get("mcp_config")
        if mcp_config_raw is None or mcp_config_raw == "":
            mcp_servers = []
        else:
            parsed = json.loads(mcp_config_raw)
            mcp_servers = [
                McpServerConfig(
                    name=key,
                    transport=value.get("transport", "stdio"),
                    command=value.get("command"),
                    args=value.get("args"),
                    url=value.get("url"),
                    headers=value.get("headers"),
                )
                for key, value in parsed.items()
            ]
        ollama_base_url_raw = data.get("ollama_base_url")
        ollama_base_url = (
            str(ollama_base_url_raw).strip() or None
            if ollama_base_url_raw
            else None
        )
        return cls(
            id=UUID(str(data["id"])),
            name=str(data["name"]),
            provider=LlmProvider(str(data["provider"])),
            model=str(data["model"]),
            agent_md=str(data["agent_md"] or ""),
            mcp_servers=mcp_servers,
            ollama_base_url=ollama_base_url,
            created_at=datetime.fromisoformat(str(data["created_at"])),
            updated_at=datetime.fromisoformat(str(data["updated_at"])),
        )


class AgentCreate(BaseModel):
    """Payload for creating a new agent. Id and timestamps are set server-side."""

    name: str
    provider: LlmProvider
    model: str
    agent_md: str = ""
    mcp_servers: list[McpServerConfig] = Field(default_factory=list)
    ollama_base_url: str | None = None

    model_config = {"from_attributes": True}


class AgentUpdate(BaseModel):
    """Payload for updating an agent. All fields optional."""

    name: str | None = None
    provider: LlmProvider | None = None
    model: str | None = None
    agent_md: str | None = None
    mcp_servers: list[McpServerConfig] | None = None
    ollama_base_url: str | None = None

    model_config = {"from_attributes": True}
