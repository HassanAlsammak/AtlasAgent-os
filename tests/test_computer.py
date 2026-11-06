import unittest
from atlasagent.computer import ComputerSession, ComputerStep, MockComputer
from atlasagent.approval import ApprovalRequired, ApprovalInvalid

class ComputerTests(unittest.TestCase):
    def setUp(self):
        self.adapter = MockComputer()
        self.session = ComputerSession(self.adapter, max_steps=3)

    def test_observe_is_read_only(self):
        self.assertIn("Mock desktop", self.session.execute(ComputerStep("observe")))
        self.assertEqual(self.adapter.events, [])

    def test_click_requires_approval(self):
        with self.assertRaises(ApprovalRequired):
            self.session.execute(ComputerStep("click", {"target": "Continue"}))
        self.assertEqual(self.adapter.events, [])

    def test_approved_click(self):
        step = ComputerStep("click", {"target": "Continue"})
        token = self.session.request(step)
        self.session.approve(token)
        self.session.execute(step, approval_token=token)
        self.assertEqual(self.adapter.events, ["click:Continue"])

    def test_cannot_reuse_approval(self):
        step = ComputerStep("click", {"target": "Continue"})
        token = self.session.request(step)
        self.session.approve(token)
        self.session.execute(step, approval_token=token)
        with self.assertRaises(ApprovalRequired):
            self.session.execute(step, approval_token=token)

    def test_cannot_change_target(self):
        token = self.session.request(ComputerStep("click", {"target": "Safe"}))
        self.session.approve(token)
        with self.assertRaises(ApprovalInvalid):
            self.session.execute(ComputerStep("click", {"target": "Delete"}), approval_token=token)

    def test_rejection(self):
        step = ComputerStep("type", {"text": "hello"})
        token = self.session.request(step)
        self.session.reject(token)
        with self.assertRaises(ApprovalInvalid):
            self.session.approve(token)

    def test_unsupported_action(self):
        with self.assertRaises(ValueError):
            self.session.request(ComputerStep("shell", {"command": "echo hello"}))

    def test_argument_validation(self):
        with self.assertRaises(ValueError):
            self.session.request(ComputerStep("scroll", {"direction": "sideways"}))

    def test_step_limit(self):
        self.session.execute(ComputerStep("observe"))
        self.session.execute(ComputerStep("observe"))
        self.session.execute(ComputerStep("observe"))
        with self.assertRaises(ValueError):
            self.session.execute(ComputerStep("observe"))

    def test_no_typed_text_in_audit(self):
        step = ComputerStep("type", {"text": "private-example"})
        token = self.session.request(step)
        self.session.approve(token)
        self.session.execute(step, approval_token=token)
        self.assertNotIn("private-example", self.session.audit_json())

if __name__ == "__main__":
    unittest.main()
