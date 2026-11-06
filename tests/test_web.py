import os
import unittest
from fastapi.testclient import TestClient
from atlasagent.web import app

class WebTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health(self):
        r = self.client.get("/api/health")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["status"], "ok")

    def test_html(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertIn("AtlasAgent OS", r.text)
        self.assertIn("nosniff", r.headers["x-content-type-options"])

    def test_offline_agents(self):
        r = self.client.post("/api/run", json={"goal": "Build a safe tool"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json()["steps"]), 3)
        self.assertEqual(r.json()["mode"], "offline")

    def test_goal_validation(self):
        r = self.client.post("/api/run", json={"goal": ""})
        self.assertEqual(r.status_code, 422)

    def test_llm_without_model(self):
        r = self.client.post("/api/run", json={"goal": "hi", "mode": "llm"})
        self.assertEqual(r.status_code, 422)

    def test_guardian(self):
        diff = "+++ b/a.py\n@@ -0,0 +1 @@\n+result = eval(user_input)"
        r = self.client.post("/api/guardian", json={"diff": diff})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["count"], 1)

    def test_guardian_empty(self):
        r = self.client.post("/api/guardian", json={"diff": ""})
        self.assertEqual(r.status_code, 422)

if __name__ == "__main__":
    unittest.main()
