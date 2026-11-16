# Atlas SI Lab — Research evaluation starter

**Status:** Experimental deterministic evaluation infrastructure, not AGI or ASI.

Atlas SI Lab runs predefined task graphs against supplied agents and reports
exact-string matches. It uses the existing `Runner` and the Python standard
library. The initial fixtures use deterministic offline example agents.

## Quick start

```bash
python examples/si_lab_demo.py
python -m unittest discover -s tests -v
```

## API

```python
from atlasagent import Task, template_agent
from atlasagent.si_lab import EvaluationCase, evaluate

case = EvaluationCase(
    "greeting",
    (Task("t1", "planner", "Hello"),),
    {"t1": "[planner] Hello"},
)
report = evaluate([case], {"planner": template_agent("planner")})
print(report.to_json())
```

The report includes a case count, number of fully passing cases, pass rate,
per-case exact match counts, and exception type when a case fails. It does not
store raw prompts or model responses. **Exact match is a narrow engineering
metric**, not a measure of intelligence, generalization, or truthfulness.

## Limits and safety

- Each case gets a new Runner, but **agent handlers themselves may retain state**.
- This is **not a sandbox**. Never evaluate untrusted code or handlers directly.
- Exceptions are recorded by type, not message, to reduce accidental disclosure.
- Case labels may contain sensitive information; use non-sensitive names.
- No external models are downloaded, trained, or invoked by default.
- No self-modification, autonomous deployment, or unrestricted computer control.

## Research progression

1. Publish versioned, reproducible task fixtures and baseline results.
2. Add semantic scoring with human-reviewed ground truth and uncertainty estimates.
3. Measure tool reliability, latency, cost, and robustness under distribution shift.
4. Add privacy, misuse, and security evaluations, including prompt-injection tests.
5. Compare agent configurations under identical budgets and conditions.

A claim of AGI or ASI would require substantially stronger, independently
validated evidence; this harness makes no such claim.
