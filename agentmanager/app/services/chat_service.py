"""Application service for generating chat responses via LangChain/LangGraph agents."""

import asyncio
import os
from uuid import UUID

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent

from agentmanager.app.models.agent import Agent, LlmProvider
from agentmanager.app.persistence.agent_repository import AgentRepository


class ChatService:
    """Builds LangChain agents from config and generates a single assistant message."""

    def __init__(self, repository: AgentRepository) -> None:
        """Initialize with an agent repository.

        Args:
            repository: The repository used to load agent config.
        """
        self._repository = repository

    def _build_llm(self, agent: Agent):
        """Build ChatOllama or ChatOpenAI from agent config."""
        if agent.provider == LlmProvider.OLLAMA:
            from langchain_ollama import ChatOllama

            base_url = (
                (agent.ollama_base_url or "").strip()
                or os.environ.get("OLLAMA_BASE_URL")
            )
            kwargs = {"model": agent.model}
            if base_url:
                kwargs["base_url"] = base_url
            return ChatOllama(**kwargs)
        if agent.provider == LlmProvider.OPENAI:
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(model=agent.model)
        raise ValueError(f"Unsupported provider: {agent.provider}")

    def _convert_to_langchain_messages(
        self, messages: list[dict[str, str]]
    ) -> list[BaseMessage]:
        """Convert API message dicts to LangChain BaseMessage list."""
        result: list[BaseMessage] = []
        for message in messages:
            role = (message.get("role") or "user").lower()
            content = message.get("content") or ""
            if role == "system":
                result.append(SystemMessage(content=content))
            elif role == "user":
                result.append(HumanMessage(content=content))
            elif role == "assistant":
                result.append(AIMessage(content=content))
            else:
                result.append(HumanMessage(content=content))
        return result

    async def _get_mcp_tools(self, agent: Agent) -> list:
        """Build MultiServerMCPClient from agent MCP config and return tools."""
        if not agent.mcp_servers:
            return []
        from langchain_mcp_adapters.client import MultiServerMCPClient

        connections: dict = {}
        for server in agent.mcp_servers:
            entry: dict = {"transport": server.transport}
            if server.command is not None:
                entry["command"] = server.command
            if server.args is not None:
                entry["args"] = server.args
            if server.url is not None:
                entry["url"] = server.url
            if server.headers is not None:
                entry["headers"] = server.headers
            connections[server.name] = entry
        client = MultiServerMCPClient(connections)
        return await client.get_tools()

    async def generate_response(
        self,
        agent_id: UUID,
        messages: list[dict[str, str]],
    ) -> str:
        """Build LLM and optional MCP tools, invoke agent, return assistant content.

        Args:
            agent_id: The agent to use.
            messages: List of {"role": "user"|"assistant"|"system", "content": "..."}.
                       Caller owns conversation; last message is typically the current user message.

        Returns:
            The next assistant message content.

        Raises:
            ValueError: If agent is not found.
            RuntimeError: If LLM or MCP invocation fails.
        """
        agent = self._repository.get_by_id(agent_id)
        if agent is None:
            raise ValueError("Agent not found")

        if not messages:
            raise ValueError("messages cannot be empty")

        llm = self._build_llm(agent)
        tools = await self._get_mcp_tools(agent)

        react_agent = create_react_agent(llm, tools)

        langchain_messages = self._convert_to_langchain_messages(messages)
        if agent.agent_md:
            langchain_messages = [
                SystemMessage(content=agent.agent_md),
                *langchain_messages,
            ]

        def run_invoke() -> str:
            result = react_agent.invoke({"messages": langchain_messages})
            result_messages = result.get("messages", [])
            for message in reversed(result_messages):
                if isinstance(message, AIMessage) and message.content:
                    return str(message.content)
            return ""

        output = await asyncio.to_thread(run_invoke)
        return output
