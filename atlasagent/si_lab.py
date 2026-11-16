"""Deterministic, offline evaluation harness for AtlasAgent OS.

This measures task outputs against exact expected strings. It does not measure
general intelligence, safety, or autonomous reasoning.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Mapping, Sequence

from .core import Agent, Runner, Task


@dataclass(frozen=True)
class EvaluationCase:
    name: str
    tasks: tuple[Task, ...]
    expected: Mapping[str, str]

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Case name must not be blank")
        ids = {task.id for task in self.tasks}
        if not self.tasks or set(self.expected) != ids:
            raise ValueError("Expected outputs must match all task IDs")


@dataclass(frozen=True)
class CaseResult:
    name: str
    passed: bool
    matched: int
    total: int
    error_type: str | None = None


@dataclass(frozen=True)
class EvaluationReport:
    cases: tuple[CaseResult, ...]

    @property
    def total(self) -> int:
        return len(self.cases)

    @property
    def passed(self) -> int:
        return sum(case.passed for case in self.cases)

    @property
    def pass_rate(self) -> float:
        return self.passed / self.total if self.total else 0.0

    def to_dict(self) -> dict:
        return {
            "schema_version": 1,
            "metric": "exact_output_match",
            "total": self.total,
            "passed": self.passed,
            "pass_rate": self.pass_rate,
            "cases": [
                {"name": c.name, "passed": c.passed, "matched": c.matched,
                 "total": c.total, "error_type": c.error_type}
                for c in self.cases
            ],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


def evaluate(
    cases: Sequence[EvaluationCase],
    agents: Mapping[str, Agent],
    *,
    max_cases: int = 100,
) -> EvaluationReport:
    """Run isolated cases; do not expose prompts or outputs in reports.

    Agents are supplied by the caller. This harness cannot sandbox custom
    handlers, so only use trusted handlers and trusted benchmark fixtures.
    """
    if not 1 <= max_cases <= 1000:
        raise ValueError("max_cases must be between 1 and 1000")
    if len(cases) > max_cases:
        raise ValueError("Evaluation case limit exceeded")
    names = [case.name for case in cases]
    if len(names) != len(set(names)):
        raise ValueError("Evaluation case names must be unique")
    results = []
    for case in cases:
        try:
            runner = Runner(dict(agents))
            outputs = runner.execute(list(case.tasks))
            matched = sum(item.output == case.expected[item.task_id] for item in outputs)
            results.append(CaseResult(case.name, matched == len(case.tasks),
                                      matched, len(case.tasks)))
        except Exception as exc:
            results.append(CaseResult(case.name, False, 0, len(case.tasks),
                                      type(exc).__name__))
    return EvaluationReport(tuple(results))
