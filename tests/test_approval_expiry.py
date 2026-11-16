"""Regression tests for time-bounded human approval tokens."""
import unittest
from unittest.mock import patch

from atlasagent.approval import ApprovalInvalid, Tool, ToolBroker


class ApprovalExpiryTests(unittest.TestCase):
    def setUp(self):
        self.calls = []
        self.broker = ToolBroker(
            {"click": Tool("click", lambda target: self.calls.append(target))},
            token_ttl_seconds=5,
        )

    def test_approved_token_expires_before_execution(self):
        with patch("atlasagent.approval.time.monotonic", return_value=100):
            token = self.broker.request_approval("click", {"target": "Safe"})
            self.broker.approve(token)
        with patch("atlasagent.approval.time.monotonic", return_value=105):
            with self.assertRaises(ApprovalInvalid):
                self.broker.invoke("click", {"target": "Safe"}, approval_token=token)
        self.assertEqual(self.calls, [])
        self.assertNotIn(token, self.broker._pending)

    def test_token_cannot_be_approved_after_expiry(self):
        with patch("atlasagent.approval.time.monotonic", return_value=100):
            token = self.broker.request_approval("click", {"target": "Safe"})
        with patch("atlasagent.approval.time.monotonic", return_value=106):
            with self.assertRaises(ApprovalInvalid):
                self.broker.approve(token)

    def test_live_token_executes_once(self):
        with patch("atlasagent.approval.time.monotonic", return_value=100):
            token = self.broker.request_approval("click", {"target": "Safe"})
            self.broker.approve(token)
        with patch("atlasagent.approval.time.monotonic", return_value=104):
            self.broker.invoke("click", {"target": "Safe"}, approval_token=token)
        self.assertEqual(self.calls, ["Safe"])

    def test_invalid_ttl_rejected(self):
        for ttl in (0, -1, 3601):
            with self.subTest(ttl=ttl):
                with self.assertRaises(ValueError):
                    ToolBroker({}, token_ttl_seconds=ttl)


if __name__ == "__main__":
    unittest.main()
