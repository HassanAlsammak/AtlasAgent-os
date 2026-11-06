# AtlasAgent OS

[![Tests](https://github.com/HassanAlsammak/AtlasAgent-os/actions/workflows/ci.yml/badge.svg)](https://github.com/HassanAlsammak/AtlasAgent-os/actions/workflows/ci.yml)

**A dependency-aware, permission-aware multi-agent orchestration starter, with experimental AtlasCode Guardian diff review.**

Python 3.10+ · MIT · Standard library only · Open source

> **Prototype:** The default agents are deterministic offline examples, not autonomous AI. An optional HTTPS chat-completions adapter is available, but you must wire it to your own handler. Guardian's rules are heuristic, not a security audit.

## Quick start

```bash
git clone https://github.com/HassanAlsammak/AtlasAgent-os.git
cd AtlasAgent-os
python -m atlasagent --goal "Plan a developer tool"
python -m unittest discover -s tests -v
```

## Features

- **Task graph:** dependencies, cycle detection and missing dependency errors.
- **Agent roles:** inject custom Python handlers for planner, builder, reviewer, or your own roles.
- **Capability allowlists:** deny unapproved capability declarations (not a sandbox).
- **Audit events:** record task outcome and execution time, without automatically recording prompts.
- **Guardian (experimental):** offline rule-based unified-diff review of added lines for selected risky patterns.
- **Provider adapter (optional):** OpenAI-compatible HTTPS chat completions with input limits and environment-based credentials.
- **CI:** unit tests on Python 3.10 and 3.12.

## Python API

```python
from atlasagent import Runner, Task, template_agent
runner = Runner({"planner": template_agent("planner"), "reviewer": template_agent("reviewer")})
results = runner.execute([
    Task("plan", "planner", "Design an open-source project"),
    Task("review", "reviewer", "Critique the plan", ("plan",)),
])
for result in results:
    print(result.role, result.output)
```

## Guardian

```python
from atlasagent.guardian import review_unified_diff
diff = """+++ b/example.py
@@ -0,0 +1 @@
+result = eval(untrusted_input)
"""
for finding in review_unified_diff(diff):
    print(finding)
```

See [Guardian usage and optional LLM adapter](docs/guardian.md).

## Security and limitations

No shell commands, code, or network calls are executed by the default runner. External agent handlers and the optional provider adapter have their own trust boundaries. Capabilities are labels, not an enforcement boundary for arbitrary custom handlers. Do not send secrets or private code to external providers without authorization. No autonomous PR commenting, sandboxed execution, persistent memory, approval UI, or vulnerability guarantee.

## Contributing and roadmap

See [CONTRIBUTING.md](CONTRIBUTING.md). Planned: explicit approval gates, redacted durable audit logs, bounded tool execution, benchmarks, and optional PR integration. Issues and tested pull requests are welcome.

MIT licensed.