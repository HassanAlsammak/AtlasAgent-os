import unittest
from atlasagent import Agent, PolicyError, Runner, Task, template_agent

class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.runner = Runner({"a": template_agent("a"), "b": template_agent("b")})

    def test_dependency_order_and_context(self):
        results = self.runner.execute([
            Task("second", "b", "review", ("first",)),
            Task("first", "a", "write"),
        ])
        self.assertIn("first: [a] write", results[0].output)
        self.assertEqual([r.task_id for r in results], ["second", "first"])
        self.assertEqual(len(self.runner.audit), 2)

    def test_cycle(self):
        with self.assertRaisesRegex(ValueError, "Cyclic"):
            self.runner.execute([Task("a", "a", "x", ("b",)), Task("b", "b", "x", ("a",))])

    def test_missing_dependency(self):
        with self.assertRaisesRegex(ValueError, "Unknown dependency"):
            self.runner.execute([Task("a", "a", "x", ("missing",))])

    def test_duplicate_id(self):
        with self.assertRaisesRegex(ValueError, "unique"):
            self.runner.execute([Task("x", "a", "x"), Task("x", "b", "y")])

    def test_permission_denied(self):
        with self.assertRaises(PolicyError):
            self.runner.execute([Task("x", "a", "x", capabilities=frozenset({"shell"}))])

    def test_permission_granted(self):
        self.runner.agents["a"] = Agent("a", lambda p, c: "ok", frozenset({"read"}))
        self.assertEqual(self.runner.execute([Task("x", "a", "x", capabilities=frozenset({"read"}))])[0].output, "ok")

    def test_output_limit(self):
        self.runner.max_output_chars = 2
        with self.assertRaisesRegex(ValueError, "Output too large"):
            self.runner.execute([Task("x", "a", "long")])
        self.assertEqual(self.runner.audit[-1]["status"], "error")

    def test_task_limit(self):
        self.runner.max_tasks = 0
        with self.assertRaisesRegex(ValueError, "Task limit"):
            self.runner.execute([Task("x", "a", "x")])

    def test_unknown_role(self):
        with self.assertRaisesRegex(ValueError, "Unknown agent"):
            self.runner.execute([Task("x", "notfound", "x")])

if __name__ == "__main__":
    unittest.main()
