import unittest
from atlasagent.approval import ApprovalRequired, ApprovalInvalid, Tool, ToolBroker

class ApprovalTests(unittest.TestCase):
    def setUp(self):
        self.calls = []
        self.broker = ToolBroker({
            "read": Tool("read", lambda value: value.upper(), side_effects=False),
            "write": Tool("write", lambda value: self.calls.append(value), side_effects=True),
        })

    def test_read_only_does_not_need_approval(self):
        self.assertEqual(self.broker.invoke("read", {"value": "hello"}), "HELLO")

    def test_write_requires_explicit_approval(self):
        with self.assertRaises(ApprovalRequired):
            self.broker.invoke("write", {"value": "hello"})
        self.assertEqual(self.calls, [])

    def test_approved_call_executes_once(self):
        token = self.broker.request_approval("write", {"value": "hello"})
        self.broker.approve(token)
        self.broker.invoke("write", {"value": "hello"}, approval_token=token)
        self.assertEqual(self.calls, ["hello"])
        with self.assertRaises(ApprovalRequired):
            self.broker.invoke("write", {"value": "hello"}, approval_token=token)

    def test_token_cannot_change_arguments(self):
        token = self.broker.request_approval("write", {"value": "safe"})
        self.broker.approve(token)
        with self.assertRaises(ApprovalInvalid):
            self.broker.invoke("write", {"value": "unsafe"}, approval_token=token)
        self.assertEqual(self.calls, [])

    def test_rejection_blocks_execution(self):
        token = self.broker.request_approval("write", {"value": "hello"})
        self.broker.reject(token)
        with self.assertRaises(ApprovalInvalid):
            self.broker.approve(token)

    def test_unapproved_token_cannot_execute(self):
        token = self.broker.request_approval("write", {"value": "hello"})
        with self.assertRaises(ApprovalRequired):
            self.broker.invoke("write", {"value": "hello"}, approval_token=token)

    def test_unknown_tool_denied(self):
        with self.assertRaises(KeyError):
            self.broker.invoke("missing", {})

    def test_read_only_approval_request_rejected(self):
        with self.assertRaises(ValueError):
            self.broker.request_approval("read", {"value": "x"})

if __name__ == "__main__":
    unittest.main()
