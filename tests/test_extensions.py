import json
import unittest
from unittest.mock import patch
from atlasagent.guardian import review_unified_diff, report_json
from atlasagent.providers import chat_completion, ProviderError

DIFF = """diff --git a/app.py b/app.py
--- a/app.py
+++ b/app.py
@@ -1,2 +1,4 @@
 import os
+password = "supersecretpassword"
+value = eval(user_input)
+safe = 1
"""

class GuardianTests(unittest.TestCase):
    def test_findings(self):
        found = review_unified_diff(DIFF)
        self.assertEqual([f.rule for f in found], ["possible-secret", "unsafe-eval"])
        self.assertEqual([f.line for f in found], [2, 3])
    def test_json(self):
        self.assertEqual(len(json.loads(report_json(DIFF))), 2)
    def test_only_added_lines(self):
        self.assertEqual(review_unified_diff("+++ b/a.py\n@@ -1 +1 @@\n-eval(x)\n+safe(x)"), [])
    def test_limit(self):
        with self.assertRaises(ValueError):
            review_unified_diff(DIFF, max_chars=2)
    def test_deleted_file(self):
        self.assertEqual(review_unified_diff("+++ /dev/null\n@@ -1 +0,0 @@\n-eval(x)"), [])

class ProviderTests(unittest.TestCase):
    def test_reject_http(self):
        with self.assertRaises(ValueError):
            chat_completion("hello", model="test", api_key="dummy", base_url="http://localhost:8000")
    def test_missing_key(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(ProviderError):
                chat_completion("hello", model="test")
    def test_prompt_limit(self):
        with self.assertRaises(ValueError):
            chat_completion("a"*30001, model="test", api_key="dummy")
    def test_mock_provider(self):
        class Response:
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self, n): return b'{"choices":[{"message":{"content":"hello"}}]}'
        with patch("atlasagent.providers.urlopen", return_value=Response()) as mock:
            self.assertEqual(chat_completion("hi", model="test", api_key="dummy"), "hello")
            self.assertEqual(mock.call_count, 1)

if __name__ == "__main__":
    unittest.main()
