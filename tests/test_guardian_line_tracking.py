"""Regression tests for Guardian's unified-diff line tracking."""
import unittest

from atlasagent.guardian import review_unified_diff


class GuardianLineTrackingTests(unittest.TestCase):
    def test_indented_context_advances_line_number(self):
        diff = (
            "--- a/demo.py\n"
            "+++ b/demo.py\n"
            "@@ -10,3 +10,4 @@\n"
            "    indented context\n"
            "     deeply indented context\n"
            "+eval(user_input)\n"
        )
        findings = review_unified_diff(diff)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].line, 12)
        self.assertEqual(findings[0].rule, "unsafe-eval")

    def test_deleted_line_does_not_advance_new_file_position(self):
        diff = (
            "--- a/demo.py\n"
            "+++ b/demo.py\n"
            "@@ -3,2 +3,2 @@\n"
            "-old_value = 1\n"
            "+eval(user_input)\n"
        )
        self.assertEqual(review_unified_diff(diff)[0].line, 3)

    def test_negative_character_limit_is_rejected(self):
        with self.assertRaises(ValueError):
            review_unified_diff("", max_chars=-1)


if __name__ == "__main__":
    unittest.main()
