# Computer-use foundation (experimental)

This is an **adapter interface and approval-gated action broker**, not a working desktop-control product. A trusted application must implement `ComputerAdapter` using its own authorized automation backend (for example, an explicitly permitted browser driver). This repository does not install drivers, connect to your computer, read your screen or bypass any OS protections.

## Try the safe mock

```bash
python examples/computer_demo.py
python -m unittest discover -s tests -v
```

The example uses `MockComputer`, which never touches the actual OS. Read-only `observe` is allowed without approval. `click`, `type`, and `scroll` require separate explicit human approval for each action. Tokens are single-use and bound to exact arguments. Sessions have a bounded step count. Audit logs intentionally exclude typed text and screen content.

## Security limitations

The mock is not a production security boundary. The host must authenticate the human, show the exact action and target, enforce target allowlists, ensure the adapter cannot bypass the broker, prevent prompt injection, and isolate credentials. No persistent approvals, browser driver, screenshot understanding, sandbox, rate limits, timeouts or live desktop access are provided. Do not connect it to untrusted websites or production accounts without those controls.
