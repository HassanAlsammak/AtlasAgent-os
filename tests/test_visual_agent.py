import json
import unittest
from atlasagent.visual_agent import Decision, run_visual_session


class TestDecision(unittest.TestCase):
    def test_click_bounds(self):
        self.assertEqual(Decision.parse('{"action":"click","x":10,"y":20,"reason":"button"}', 100, 100).x, 10)
        for x in [-1, 100, True, "1"]:
            with self.assertRaises(ValueError):
                Decision.parse(json.dumps({"action": "click", "x": x, "y": 2}), 100, 100)

    def test_invalid_actions(self):
        for action in ["shell", "delete", "open_url", None]:
            with self.assertRaises(ValueError):
                Decision.parse(json.dumps({"action": action}), 100, 100)

    def test_secret_text_rejected(self):
        with self.assertRaises(ValueError):
            Decision.parse('{"action":"type","text":"password: abc"}', 100, 100)

    def test_scroll_and_done(self):
        self.assertEqual(Decision.parse('{"action":"scroll","direction":"down"}', 100, 100).direction, "down")
        self.assertEqual(Decision.parse('{"action":"done","reason":"finished"}', 100, 100).action, "done")


class FakeAdapter:
    def __init__(self):
        self.calls = []

    def capture(self):
        self.calls.append("capture")
        return b"png", 100, 100

    def click(self, target):
        self.calls.append(("click", target))
        return "clicked"

    def type(self, text):
        self.calls.append(("type", text))
        return "typed"

    def scroll(self, direction):
        self.calls.append(("scroll", direction))
        return "scrolled"


class TestSession(unittest.TestCase):
    def test_human_rejection_stops(self):
        adapter = FakeAdapter()
        events = run_visual_session("test", adapter,
            lambda *args: Decision("click", "test", 1, 2), lambda d: False)
        self.assertEqual(adapter.calls, ["capture"])
        self.assertIn("rejected", events[0])

    def test_approved_action_then_done(self):
        adapter = FakeAdapter()
        decisions = iter([Decision("click", "button", 1, 2), Decision("done", "finished")])
        events = run_visual_session("test", adapter, lambda *args: next(decisions), lambda d: True)
        self.assertEqual(adapter.calls, ["capture", ("click", "1,2"), "capture"])
        self.assertEqual(events[0], "clicked")

    def test_max_steps(self):
        with self.assertRaises(ValueError):
            run_visual_session("test", FakeAdapter(), lambda *args: None, lambda d: True, max_steps=31)
