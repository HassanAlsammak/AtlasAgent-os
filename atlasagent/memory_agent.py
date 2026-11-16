"""Opt-in read-only memory context for AtlasAgent handlers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .core import Agent
from .memory import LocalMemory


@dataclass(frozen=True)
class MemoryContextConfig:
    namespace: str
    query: str = ""
    limit: int = 5
    max_context_chars: int = 2000

    def __post_init__(self) -> None:
        LocalMemory._validate_namespace(self.namespace)
        if not isinstance(self.query, str):
            raise ValueError("query must be text")
        if not 1 <= self.limit <= 20:
            raise ValueError("limit must be between 1 and 20")
        if not 1 <= self.max_context_chars <= 10000:
            raise ValueError("max_context_chars must be between 1 and 10000")


def with_memory_context(agent: Agent, memory: LocalMemory, config: MemoryContextConfig) -> Agent:
    """Wrap a trusted agent with explicitly configured, read-only memory lookup.

    Notes are untrusted data, never instructions or tool permissions.
    No prompt or output is saved automatically.
    """
    if not isinstance(agent, Agent):
        raise TypeError("agent must be an Agent")

    def handle(prompt: str, context: Mapping[str, str]) -> str:
        if "atlas_memory" in context:
            raise ValueError("Reserved context key: atlas_memory")
        entries = memory.search(config.namespace, config.query, limit=config.limit)
        chunks: list[str] = []
        remaining = config.max_context_chars
        for entry in entries:
            if remaining <= 0:
                break
            note = entry.content[:remaining]
            chunks.append(note)
            remaining -= len(note)
            if remaining > 0:
                remaining -= min(remaining, 5)
        enriched = dict(context)
        enriched["atlas_memory"] = "\n---\n".join(chunks)[:config.max_context_chars]
        return agent.handler(prompt, enriched)

    return Agent(role=agent.role, handler=handle, capabilities=agent.capabilities)
