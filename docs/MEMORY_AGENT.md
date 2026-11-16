# Atlas Memory Agent Integration

Optional read-only integration between the existing SQLite `LocalMemory` and
the existing dependency-aware `Runner`. Memory is read **only when explicitly
configured**. It never saves prompts or responses automatically.

```python
from atlasagent import Runner, Task, template_agent
from atlasagent.memory import LocalMemory
from atlasagent.memory_agent import MemoryContextConfig, with_memory_context

with LocalMemory("notes.sqlite3") as memory:
    memory.add("demo", "Prefer unit tests")
    planner = with_memory_context(
        template_agent("planner"), memory, MemoryContextConfig("demo")
    )
    results = Runner({"planner": planner}).execute(
        [Task("plan", "planner", "Plan the project")]
    )
    print(results[0].output)
```

**Limitations:** Notes are plain text, not encrypted. Namespaces are logical
partitions, not access controls. Retrieved notes are untrusted data and must
not be used as instructions or permissions. The wrapper does not sandbox
handlers, is not semantic search, and does not confer general intelligence.
Callers own database lifecycle and must obtain consent before saving personal
data. The `atlas_memory` context key is reserved.

Run: `python -m unittest discover -s tests -v`.
