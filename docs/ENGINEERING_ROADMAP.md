# AtlasAgent OS — Engineering Roadmap

This roadmap describes **proposals**, not shipped features. Each milestone requires tests, documentation, and a reproducible demonstration before release.

## Current baseline (v0.3.0)

- Dependency-aware task orchestration and configurable handlers.
- Experimental unified-diff Guardian heuristics.
- Approval-gated mock computer-use and opt-in local desktop CLI.
- Local web workspace; **do not expose the demo to the public Internet**.
- Optional HTTPS chat-completions provider adapter.

## Milestone 1 — Reliability and security

- [ ] Add reproducible benchmark fixtures for graph execution, permission denial, and failure recovery.
- [ ] Test approval-token expiry, one-time use, argument binding, and denial cases.
- [ ] Redact credentials and private content from durable audit events.
- [ ] Run static analysis, dependency review, and secret scanning in CI.
- [ ] Keep GitHub Actions permissions read-only by default; pin third-party actions to commit SHAs.
- [ ] Document threat models for local handlers, remote models, web endpoints, and desktop control.

**Exit criteria:** clean CI, documented threat model, tests for all approval paths, and no credentials in example logs.

## Milestone 2 — Safe desktop assistance

- [ ] Define a typed desktop action protocol with dry-run mode and bounded execution.
- [ ] Implement explicit per-action user approval, visible stop control, and allowlisted targets.
- [ ] Isolate sensitive actions (payments, account settings, deletion, credential entry).
- [ ] Add screenshot-based observation only with opt-in capture and privacy controls.
- [ ] Provide Windows installation and troubleshooting documentation.

**Exit criteria:** scripted end-to-end demo, verified cancellation behavior, and no silent privileged actions.

## Milestone 3 — Developer assistant and Guardian

- [ ] Parse changed files and classify findings by confidence and severity.
- [ ] Add deterministic rule fixtures and false-positive/false-negative evaluation.
- [ ] Provide optional AI explanations with clear disclosure and no automatic secret uploads.
- [ ] Draft pull requests for human review; never merge automatically by default.

**Exit criteria:** public evaluation dataset, reproducible metrics, and reviewer-controlled changes.

## Milestone 4 — Accessibility and integrations

- [ ] Arabic and English interface, including right-to-left layout checks.
- [ ] Local model integration and explicit provider cost/latency reporting.
- [ ] Documented plugin permissions and integration test harness.
- [ ] Signed release artifacts and clear upgrade/rollback instructions.

## Comparative benchmarks

Compare against relevant OpenClaw and Hermes Agent workflows only with the **same hardware, model, task definitions, and permission constraints**. Report task success rate, median runtime, cost, approval count, and security failures. Publish unsuccessful runs as well as successful ones. Do not claim superiority without evidence.

## Contribution standards

Every change should include a narrowly scoped issue or PR, tests for behavior changes, updated documentation, and a clear statement of security impact. Respect upstream licenses and attribution when reusing code.
