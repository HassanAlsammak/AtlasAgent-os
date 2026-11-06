# Human approval gates (experimental)

`ToolBroker` is a small in-process guard for tool calls. **It is not a sandbox or a complete authentication/authorization system.** Only register trusted handlers. The caller is responsible for displaying the exact tool name and arguments to a real human and calling `approve(token)` only after consent.

```python
from atlasagent.approval import Tool, ToolBroker

broker = ToolBroker({"save": Tool("save", lambda text: print("SAVED:", text))})
args = {"text": "A draft note"}
token = broker.request_approval("save", args)
print("Approve save with arguments:", args)
# Obtain actual human confirmation in your application UI.
broker.approve(token)  # ONLY after confirmation
broker.invoke("save", args, approval_token=token)
```

Approvals bind to the exact JSON-serializable arguments and tool name and are consumed once before invoking the handler. Rejected or modified requests cannot execute using the original approval. Tokens live in memory and are lost on restart.

## Limitations

- No user identity, multi-user isolation, expiry, persistent approval store, or external authentication.
- Handler functions can perform arbitrary actions outside the broker.
- No tool sandbox, timeout, retries, rate limiting, or audit persistence.
- Never auto-approve in an autonomous agent. Use a trusted UI to collect consent.
