# AtlasCode Guardian (experimental)

Guardian scans *added lines* of a unified Git diff and emits conservative, rule-based findings. It is not a complete security scanner and may report false positives or miss vulnerabilities.

## Offline example

```bash
git diff --no-ext-diff HEAD~1 HEAD > changes.diff
python -c "from pathlib import Path; from atlasagent.guardian import report_json; print(report_json(Path('changes.diff').read_text()))"
```

Checks include possible hard-coded credentials, eval/exec, shell=True and pickle deserialization. It does not execute any submitted code, send your diff to an AI service, post PR comments or modify files.

## Optional model adapter

```bash
export ATLASAGENT_API_KEY="your-provider-key"
python -c "from atlasagent.providers import chat_completion; print(chat_completion('Suggest three unit tests', model='your-model'))"
```

The provider must expose an HTTPS OpenAI-compatible /chat/completions endpoint. Using the provider can incur costs and transmits your prompt to that provider. Do not submit private source code without authorization. This adapter does not automatically connect the agent runner to the model; callers must explicitly supply a handler.
