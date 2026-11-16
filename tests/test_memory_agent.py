import tempfile
from pathlib import Path
import unittest

from atlasagent.core import Agent, Runner, Task
from atlasagent.memory import LocalMemory
from atlasagent.memory_agent import MemoryContextConfig, with_memory_context


class MemoryAgentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.memory = LocalMemory(Path(self.temp.name) / "memory.sqlite3")

    def tearDown(self):
        self.memory.close()
        self.temp.cleanup()

    def test_opt_in_context_in_runner(self):
        self.memory.add("project", "Use Python")
        agent = Agent("planner", lambda prompt, ctx: ctx["atlas_memory"])
        wrapped = with_memory_context(agent, self.memory, MemoryContextConfig("project"))
        results = Runner({"planner": wrapped}).execute([Task("plan", "planner", "Plan")])
        self.assertEqual(results[0].output, "Use Python")

    def test_no_automatic_write(self):
        agent = Agent("planner", lambda prompt, ctx: "result")
        wrapped = with_memory_context(agent, self.memory, MemoryContextConfig("project"))
        Runner({"planner": wrapped}).execute([Task("plan", "planner", "secret prompt")])
        self.assertEqual(self.memory.search("project"), [])

    def test_namespace_and_truncation(self):
        self.memory.add("other", "private")
        self.memory.add("project", "123456789")
        agent = Agent("planner", lambda prompt, ctx: ctx["atlas_memory"])
        wrapped = with_memory_context(agent, self.memory, MemoryContextConfig("project", max_context_chars=4))
        self.assertEqual(wrapped.handler("", {}), "1234")

    def test_preserves_capabilities(self):
        agent = Agent("planner", lambda prompt, ctx: "ok", frozenset({"read"}))
        wrapped = with_memory_context(agent, self.memory, MemoryContextConfig("project"))
        self.assertEqual(wrapped.capabilities, frozenset({"read"}))

    def test_rejects_reserved_context_key(self):
        agent = Agent("planner", lambda prompt, ctx: "ok")
        wrapped = with_memory_context(agent, self.memory, MemoryContextConfig("project"))
        with self.assertRaises(ValueError):
            wrapped.handler("", {"atlas_memory": "injected"})

    def test_config_limits(self):
        for config in [dict(namespace=""), dict(namespace="x", limit=0),
                       dict(namespace="x", limit=21), dict(namespace="x", max_context_chars=0)]:
            with self.subTest(config=config):
                with self.assertRaises(ValueError):
                    MemoryContextConfig(**config)


if __name__ == "__main__":
    unittest.main()
