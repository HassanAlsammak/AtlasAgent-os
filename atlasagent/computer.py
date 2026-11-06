"""Constrained computer-use orchestration with explicit approval for mutations.

This module does not control a real desktop by itself. Applications supply a
trusted adapter implementing the protocol. Never pass untrusted adapters.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, Any, Mapping
import json

from .approval import Tool, ToolBroker, ApprovalRequired

ALLOWED_ACTIONS = frozenset({"observe", "click", "type", "scroll"})
MUTATIONS = frozenset({"click", "type", "scroll"})

class ComputerAdapter(Protocol):
    def observe(self) -> str: ...
    def click(self, target: str) -> str: ...
    def type(self, text: str) -> str: ...
    def scroll(self, direction: str) -> str: ...

@dataclass(frozen=True)
class ComputerStep:
    action: str
    arguments: Mapping[str, str] = field(default_factory=dict)

    def validate(self) -> None:
        if self.action not in ALLOWED_ACTIONS:
            raise ValueError("Unsupported computer action")
        expected = {
            "observe": set(), "click": {"target"},
            "type": {"text"}, "scroll": {"direction"},
        }[self.action]
        if set(self.arguments) != expected:
            raise ValueError("Invalid arguments for action")
        if any(not isinstance(v, str) or len(v) > 2000 for v in self.arguments.values()):
            raise ValueError("Arguments must be strings up to 2000 characters")
        if self.action == "scroll" and self.arguments["direction"] not in {"up", "down"}:
            raise ValueError("Scroll direction must be up or down")

@dataclass
class ComputerSession:
    adapter: ComputerAdapter
    max_steps: int = 25
    history: list[dict[str, Any]] = field(default_factory=list)
    _steps_used: int = 0

    def __post_init__(self) -> None:
        if not 1 <= self.max_steps <= 100:
            raise ValueError("max_steps must be 1-100")
        self._broker = ToolBroker({
            "observe": Tool("observe", self.adapter.observe, side_effects=False),
            "click": Tool("click", self.adapter.click),
            "type": Tool("type", self.adapter.type),
            "scroll": Tool("scroll", self.adapter.scroll),
        })

    def request(self, step: ComputerStep) -> str | None:
        step.validate()
        if self._steps_used >= self.max_steps:
            raise ValueError("Computer session step limit exceeded")
        if step.action == "observe":
            return None
        return self._broker.request_approval(step.action, dict(step.arguments))

    def approve(self, token: str) -> None:
        """Call only after an actual human has reviewed the step."""
        self._broker.approve(token)

    def reject(self, token: str) -> None:
        self._broker.reject(token)

    def execute(self, step: ComputerStep, *, approval_token: str | None = None) -> str:
        step.validate()
        if self._steps_used >= self.max_steps:
            raise ValueError("Computer session step limit exceeded")
        result = self._broker.invoke(step.action, dict(step.arguments), approval_token=approval_token)
        self._steps_used += 1
        if not isinstance(result, str):
            raise TypeError("Computer adapter must return a string")
        # Deliberately omit typed text and observation content from logs.
        self.history.append({"action": step.action, "status": "ok"})
        return result

    def audit_json(self) -> str:
        return json.dumps(self.history, indent=2)

class MockComputer:
    """Deterministic adapter for tests and demonstrations; no OS access."""
    def __init__(self) -> None:
        self.events: list[str] = []

    def observe(self) -> str:
        return "Mock desktop: one button labeled Continue"

    def click(self, target: str) -> str:
        self.events.append("click:" + target)
        return "Clicked " + target

    def type(self, text: str) -> str:
        self.events.append("type:" + text)
        return "Typed text"

    def scroll(self, direction: str) -> str:
        self.events.append("scroll:" + direction)
        return "Scrolled " + direction
