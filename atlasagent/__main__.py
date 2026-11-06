import argparse
from .core import Runner, Task, template_agent

def main():
    parser = argparse.ArgumentParser(description="AtlasAgent OS offline demo")
    parser.add_argument("--goal", default="Design a useful open-source AI agent project")
    args = parser.parse_args()
    runner = Runner(agents={r: template_agent(r) for r in ("planner", "builder", "reviewer")})
    tasks = [
        Task("plan", "planner", args.goal),
        Task("build", "builder", "Create an implementation plan", ("plan",)),
        Task("review", "reviewer", "Review the implementation plan", ("build",)),
    ]
    for result in runner.execute(tasks):
        print(f"{result.role}: {result.output}")

if __name__ == "__main__":
    main()
