# Open-source project overview

**Project:** AtlasAgent OS  
**Repository:** https://github.com/HassanAlsammak/AtlasAgent-os  
**Maintainer:** HassanAlsammak  
**License:** MIT  
**Language:** Python 3.10+

## What it does today

AtlasAgent OS is a small, auditable multi-agent orchestration prototype for
developer workflows. It provides dependency-aware task graphs, configurable
agent handlers, capability allowlists, basic audit events, a local web demo,
and experimental Guardian diff analysis. It includes optional local desktop
actions with explicit approval, a configurable remote-model adapter, SQLite
note storage, and a deterministic Atlas SI Lab evaluation harness.

The default agents are offline deterministic examples. The project is not AGI,
ASI, or a production-grade autonomous coding agent. Capability labels do not
sandbox arbitrary Python handlers. The web demo should remain localhost-only.

## Reproduce a baseline

```bash
git clone https://github.com/HassanAlsammak/AtlasAgent-os.git
cd AtlasAgent-os
python -m pip install -e ".[web,test]"
python -m unittest discover -s tests -v
python -m atlasagent --goal "Plan a developer tool"
python examples/si_lab_demo.py
```

The test suite runs on Python 3.10 and 3.12 in GitHub Actions. Check current
workflow results before making a claim that all tests pass.

## Why support would help

Codex assistance could help review and test pull requests, strengthen approval
and tool boundaries, identify regressions, expand reproducible benchmarks,
improve Arabic/English developer documentation, and make the project easier
for contributors to use. API access could enable *opt-in* comparisons of
model-backed handlers under consistent test conditions, with cost and privacy
controls.

## 90-day development plan

- **Days 1–30:** stabilize test suite, document trust boundaries, publish
  reproducible examples and initial benchmark outcomes.
- **Days 31–60:** add optional model-backed evaluation with explicit cost,
  latency, and privacy reporting; add negative tests for prompt injection.
- **Days 61–90:** improve contributor onboarding, multilingual documentation,
  and human-reviewed developer workflows.

All proposed features are goals, not shipped capabilities.

## Suggested application summary

> I maintain AtlasAgent OS, an MIT-licensed Python project exploring auditable
> multi-agent orchestration, developer automation, and reproducible evaluation.
> It currently includes a dependency-aware task runner, experimental code-diff
> analysis, human approval mechanisms, local memory, and an offline evaluation
> harness. I would use Codex to strengthen tests and security, improve
> documentation, and build reliable, human-reviewed workflows for open-source
> contributors. Repository: https://github.com/HassanAlsammak/AtlasAgent-os

Do not claim a particular number of users, downloads, contributors, or stars
without checking GitHub first.
