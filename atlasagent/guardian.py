"""Conservative offline diff review; findings are leads, not security verdicts."""
from __future__ import annotations
from dataclasses import dataclass, asdict
import json
import re

@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    rule: str
    severity: str
    message: str

_RULES = (
    ("possible-secret", "high", re.compile(r"""(?i)\b(?:api[_-]?key|secret|password|access[_-]?token)\s*[:=]\s*['"][^'"]{8,}['"]"""), "Possible hard-coded credential; use a secret store."),
    ("shell-true", "high", re.compile(r"\bshell\s*=\s*True\b"), "Shell execution enabled; verify trust boundaries."),
    ("unsafe-eval", "high", re.compile(r"\b(?:eval|exec)\s*\("), "Dynamic execution detected; review input provenance."),
    ("pickle-load", "medium", re.compile(r"\bpickle\.(?:load|loads)\s*\("), "Pickle deserialization is unsafe for untrusted data."),
)

def review_unified_diff(diff: str, *, max_chars: int = 1_000_000) -> list[Finding]:
    if len(diff) > max_chars:
        raise ValueError("Diff exceeds review limit")
    findings: list[Finding] = []
    path = ""
    line = 0
    for raw in diff.splitlines():
        if raw.startswith("+++ b/"):
            path = raw[6:]
        elif raw.startswith("+++ /dev/null"):
            path = ""
        elif raw.startswith("@@"):
            match = re.search(r"\+(\d+)(?:,(\d+))?", raw)
            if match:
                line = int(match.group(1))
        elif raw.startswith("+") and not raw.startswith("+++"):
            content = raw[1:]
            if path and not path.endswith((".md", ".rst", ".txt", ".lock")):
                for rule, severity, pattern, message in _RULES:
                    if pattern.search(content):
                        findings.append(Finding(path, line, rule, severity, message))
            line += 1
        elif raw.startswith(" ") and not raw.startswith("    "):
            line += 1
    return findings

def report_json(diff: str) -> str:
    return json.dumps([asdict(item) for item in review_unified_diff(diff)], indent=2)
