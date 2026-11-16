import tempfile
from pathlib import Path
import unittest

from atlasagent.memory import LocalMemory


class MemoryTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = Path(self.directory.name) / "notes.sqlite3"
        self.memory = LocalMemory(self.path)

    def tearDown(self):
        self.memory.close()
        self.directory.cleanup()

    def test_add_search_delete(self):
        memory_id = self.memory.add("project", "Build an agent")
        self.assertEqual(self.memory.search("project", "agent")[0].id, memory_id)
        self.assertTrue(self.memory.delete("project", memory_id))
        self.assertFalse(self.memory.delete("project", memory_id))
        self.assertEqual(self.memory.search("project"), [])

    def test_namespace_isolation(self):
        memory_id = self.memory.add("private", "internal note")
        self.assertEqual(self.memory.search("public"), [])
        self.assertFalse(self.memory.delete("public", memory_id))
        self.assertEqual(len(self.memory.search("private")), 1)

    def test_persists_between_connections(self):
        self.memory.add("atlas", "persistent")
        with LocalMemory(self.path) as second:
            self.assertEqual(second.search("atlas")[0].content, "persistent")

    def test_literal_search_not_sql_wildcards(self):
        self.memory.add("atlas", "100% done")
        self.memory.add("atlas", "other")
        self.assertEqual(len(self.memory.search("atlas", "%")), 1)
        self.assertEqual(len(self.memory.search("atlas", "DONE")), 1)

    def test_limits_and_validation(self):
        with self.assertRaises(ValueError):
            self.memory.add("", "note")
        with self.assertRaises(ValueError):
            self.memory.add("atlas", " ")
        with self.assertRaises(ValueError):
            self.memory.search("atlas", limit=0)
        with self.assertRaises(ValueError):
            self.memory.delete("atlas", -1)
        with self.assertRaises(ValueError):
            LocalMemory(self.path, max_chars=0)

    def test_recent_first_and_limit(self):
        first = self.memory.add("atlas", "first")
        last = self.memory.add("atlas", "last")
        self.assertEqual([x.id for x in self.memory.search("atlas", limit=1)], [last])
        self.assertNotEqual(first, last)


if __name__ == "__main__":
    unittest.main()
