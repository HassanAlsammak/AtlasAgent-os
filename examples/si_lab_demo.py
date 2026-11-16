"""Run with: python examples/si_lab_demo.py"""
from atlasagent import Task, template_agent
from atlasagent.si_lab import EvaluationCase, evaluate

case = EvaluationCase(
    name="offline-planning-smoke-test",
    tasks=(Task("plan", "planner", "Plan a small application"),),
    expected={"plan": "[planner] Plan a small application"},
)
report = evaluate([case], {"planner": template_agent("planner")})
print(report.to_json())
