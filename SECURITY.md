# Security policy

AtlasAgent OS is an experimental developer tool. It is **not** a security
boundary, a sandbox, or a production-ready autonomous agent.

## Reporting a vulnerability

Please **do not** open a public issue with exploit details, credentials, or
personal information. Use GitHub's **Report a vulnerability** / private
vulnerability reporting feature if enabled for this repository. If it is not
enabled, open a public issue requesting a private reporting channel **without**
including the vulnerability details.

Include affected version/commit, minimal reproduction, expected versus actual
behavior, and impact when communicating privately. Maintainers will triage
reports as availability permits; no response-time SLA is promised.

## Trust boundaries

- The default runner uses deterministic offline handlers. Third-party Python
  handlers run with the privileges of the host process; capability labels are
  not sandbox enforcement.
- Remote model adapters may send prompts to an external provider when explicitly
  configured. Never send credentials or confidential data without authorization.
- The local web workspace is for localhost development; do not publish it to
  the Internet without independent authentication, authorization, and review.
- Desktop automation requires human authorization and must not be treated as a
  general-purpose safety guarantee.
- SQLite memory is unencrypted. Do not store secrets or sensitive user data.
- Retrieved content and model output are untrusted; do not execute them or
  interpret them as authorization.

## Supported versions

Only the current `main` branch receives best-effort fixes. No stable security
support or guaranteed patch cadence is offered.

## Security checklist for contributions

1. Avoid secrets in commits, logs, fixtures, and screenshots.
2. Add negative tests for permission checks and failure paths.
3. Require human review before external actions or merges.
4. Document data retention, provider calls, and known limitations.
