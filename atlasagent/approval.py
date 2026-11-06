"""Explicit human approval gates for side-effecting tool calls.

A token is bound to a single tool name and exact argument payload.
The broker never auto-approves; callers must obtain consent out-of-band.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Any
import hashlib
import json
import secrets

class ApprovalRequired(PermissionError):
    pass

class ApprovalInvalid(PermissionError):
    pass

def _digest(name: str, args: dict[str, Any]) -> str:
    canonical = json.dumps({"tool": name, "args": args}, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

@dataclass(frozen=True)
class Tool:
    name: str
    handler: Callable[..., Any]
    side_effects: bool = True

@dataclass
class ToolBroker:
    tools: dict[str, Tool]
    _pending: dict[str, str] = field(default_factory=dict, repr=False)
    _approved: set[str] = field(default_factory=set, repr=False)

    def request_approval(self, name: str, args: dict[str, Any]) -> str:
        tool = self._get(name)
        if not tool.side_effects:
            raise ValueError("Read-only tools do not require approval")
        fingerprint = _digest(name, args)
        token = secrets.token_urlsafe(32)
        self._pending[token] = fingerprint
        return token

    def approve(self, token: str) -> None:
        if token not in self._pending:
            raise ApprovalInvalid("Unknown approval token")
        self._approved.add(token)

    def reject(self, token: str) -> None:
        self._pending.pop(token, None)
        self._approved.discard(token)

    def invoke(self, name: str, args: dict[str, Any], *, approval_token: str | None = None) -> Any:
        tool = self._get(name)
        if tool.side_effects:
            if approval_token is None or approval_token not in self._approved:
                raise ApprovalRequired("Explicit human approval required")
            fingerprint = _digest(name, args)
            if self._pending.get(approval_token) != fingerprint:
                raise ApprovalInvalid("Approval does not match this call")
            # Consume before invocation: even failed operations require a new approval.
            self._approved.remove(approval_token)
            del self._pending[approval_token]
        return tool.handler(**args)

    def _get(self, name: str) -> Tool:
        if name not in self.tools:
            raise KeyError(f"Unknown tool: {name}")
        return self.tools[name]
