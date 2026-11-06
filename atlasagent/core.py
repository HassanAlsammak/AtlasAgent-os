"""Dependency-aware, permission-aware offline multi-agent orchestration."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Mapping
import json
import time

class PolicyError(Exception):
    """Task requests a capability not granted to its agent."""

@dataclass(frozen=True)
class Task:
    id: str
    role: str
    prompt: str
    depends_on: tuple[str, ...] = ()
    capabilities: frozenset[str] = frozenset()

@dataclass
class Result:
    task_id: str
    role: str
    output: str
    elapsed_ms: int

@dataclass
class Agent:
    role: str
    handler: Callable[[str, Mapping[str, str]], str]
    capabilities: frozenset[str] = frozenset()

@dataclass
class Runner:
    agents: dict[str, Agent]
    max_tasks: int = 100
    max_output_chars: int = 100_000
    audit: list[dict] = field(default_factory=list)

    def execute(self, tasks: list[Task]) -> list[Result]:
        if len(tasks) > self.max_tasks:
            raise ValueError("Task limit exceeded")
        ids = [t.id for t in tasks]
        if len(ids) != len(set(ids)) or any(not x for x in ids):
            raise ValueError("Task IDs must be unique and nonempty")
        lookup = {t.id: t for t in tasks}
        for task in tasks:
            if task.role not in self.agents:
                raise ValueError(f"Unknown agent: {task.role}")
            if any(dep not in lookup for dep in task.depends_on):
                raise ValueError(f"Unknown dependency in {task.id}")
            if not task.capabilities <= self.agents[task.role].capabilities:
                raise PolicyError(f"Capabilities not permitted for {task.id}")
        done: dict[str, Result] = {}
        pending = dict(lookup)
        while pending:
            ready = [t for t in pending.values() if all(dep in done for dep in t.depends_on)]
            if not ready:
                raise ValueError("Cyclic task dependencies")
            for task in ready:
                context = {dep: done[dep].output for dep in task.depends_on}
                start = time.monotonic()
                try:
                    output = self.agents[task.role].handler(task.prompt, context)
                    if not isinstance(output, str):
                        raise TypeError("Agent handler must return text")
                    if len(output) > self.max_output_chars:
                        raise ValueError("Output too large")
                    result = Result(task.id, task.role, output, round((time.monotonic()-start)*1000))
                    done[task.id] = result
                    self.audit.append({"task_id": task.id, "role": task.role, "status": "ok", "elapsed_ms": result.elapsed_ms})
                    del pending[task.id]
                except Exception as exc:
                    self.audit.append({"task_id": task.id, "role": task.role, "status": "error", "error_type": type(exc).__name__})
                    raise
        return [done[task.id] for task in tasks]

    def audit_json(self) -> str:
        return json.dumps(self.audit, indent=2)

def template_agent(role: str) -> Agent:
    """Offline deterministic example; never calls a model or executes code."""
    def handle(prompt: str, context: Mapping[str, str]) -> str:
        previous = " | ".join(f"{key}: {value}" for key, value in context.items())
        return f"[{role}] {prompt}" + (f" | Context: {previous}" if previous else "")
    return Agent(role=role, handler=handle)
