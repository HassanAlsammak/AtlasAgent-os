import json
import unittest

from atlasagent import Agent, Task, template_agent
from atlasagent.si_lab import EvaluationCase, evaluate


class SILabTests(unittest.TestCase):
    def test_passing_case_and_json(self):
        case = EvaluationCase("basic", (Task("a", "planner", "Hello"),),
                              {"a": "[planner] Hello"})
        report = evaluate([case], {"planner": template_agent("planner")})
        self.assertEqual(report.passed, 1)
        self.assertEqual(report.pass_rate, 1.0)
        self.assertEqual(json.loads(report.to_json())["metric"], "exact_output_match")

    def test_mismatch_is_failure(self):
        case = EvaluationCase("wrong", (Task("a", "planner", "Hello"),),
                              {"a": "wrong"})
        report = evaluate([case], {"planner": template_agent("planner")})
        self.assertEqual(report.cases[0].matched, 0)
        self.assertFalse(report.cases[0].passed)

    def test_dependency_chain(self):
        tasks = (Task("a", "planner", "Start"),
                 Task("b", "reviewer", "Review", ("a",)))
        expected = {"a": "[planner] Start",
                    "b": "[reviewer] Review | Context: a: [planner] Start"}
        case = EvaluationCase("chain", tasks, expected)
        report = evaluate([case], {"planner": template_agent("planner"),
                                   "reviewer": template_agent("reviewer")})
        self.assertEqual(report.passed, 1)

    def test_error_is_recorded_without_prompt(self):
        secret = "sensitive-test-value"
        def broken(prompt, context):
            raise RuntimeError(secret)
        case = EvaluationCase("error", (Task("a", "bad", secret),),
                              {"a": "ok"})
        report = evaluate([case], {"bad": Agent("bad", broken)})
        self.assertEqual(report.cases[0].error_type, "RuntimeError")
        self.assertNotIn(secret, report.to_json())

    def test_invalid_cases(self):
        with self.assertRaises(ValueError):
            EvaluationCase("", (Task("a", "x", "hi"),), {"a": "hi"})
        with self.assertRaises(ValueError):
            EvaluationCase("missing", (Task("a", "x", "hi"),), {})
        with self.assertRaises(ValueError):
            evaluate([], {}, max_cases=0)

    def test_duplicate_names_and_case_limit(self):
        case = EvaluationCase("same", (Task("a", "x", "hi"),), {"a": "hi"})
        with self.assertRaises(ValueError):
            evaluate([case, case], {"x": template_agent("x")})
        with self.assertRaises(ValueError):
            evaluate([case, case], {}, max_cases=1)

    def test_empty_report(self):
        report = evaluate([], {})
        self.assertEqual(report.total, 0)
        self.assertEqual(report.pass_rate, 0.0)


if __name__ == "__main__":
    unittest.main()
